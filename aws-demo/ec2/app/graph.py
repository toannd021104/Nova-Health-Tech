"""LangGraph workflow for the Nova clinical assistant.

Two-lane design as described in docs/architecture/fine_tuning_and_distillation.md:
  - classifier decides emergency vs complex
  - emergency → Claude Haiku 4.5 (fast path)
  - complex   → Claude Sonnet 4.5 (teacher)

RAG retrieval runs on both lanes. LangChain/LangGraph end-to-end — boto3 is used
only by the rag module for S3 object listing.
"""
from __future__ import annotations

import logging
import os
from typing import TypedDict, Literal

from langchain_aws import ChatBedrockConverse
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END

from rag import retriever

log = logging.getLogger("graph")

REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
FAST_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0"
)
TEACHER_MODEL_ID = os.environ.get(
    "BEDROCK_TEACHER_MODEL_ID",
    "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
)

# Low-variance hyperparameters per docs/architecture/fine_tuning_and_distillation.md.
# Claude (via Bedrock Converse) rejects specifying both temperature AND top_p, so
# we set temperature only. Temperature near 0 already gives consistent tone.
_fast = ChatBedrockConverse(
    model=FAST_MODEL_ID,
    region_name=REGION,
    temperature=0.1,
    max_tokens=700,
)
_teacher = ChatBedrockConverse(
    model=TEACHER_MODEL_ID,
    region_name=REGION,
    temperature=0.2,
    max_tokens=1500,
)
_classifier = ChatBedrockConverse(
    model=FAST_MODEL_ID,
    region_name=REGION,
    temperature=0.0,
    max_tokens=8,
)

SYSTEM_PROMPT = (
    "You are Nova Health Tech's clinical decision-support assistant.\n"
    "Voice: precise, neutral, professional. No filler phrases.\n"
    "Structure every answer as:\n"
    "  1. Immediate action (one sentence, only for emergency questions)\n"
    "  2. Key details (3–5 bullets, each with a citation token like [1], [2])\n"
    "  3. Cautions / contraindications\n"
    "  4. References (the citation list, mapping [1], [2] to the retrieved sources)\n"
    "Never include advice for patients directly. This is decision support, "
    "not a diagnosis.\n"
    "If the retrieved context does not support a claim, say so rather than guess."
)


class AssistantState(TypedDict, total=False):
    question: str
    route: Literal["emergency", "complex"]
    context: str
    citations: list[dict]
    answer: str


def classify(state: AssistantState) -> AssistantState:
    """Tiny classifier: returns 'emergency' or 'complex'."""
    q = state["question"]
    reply = _classifier.invoke(
        [
            SystemMessage(
                content=(
                    "Classify the clinical query as one word: "
                    "'emergency' for acute/time-critical (sepsis, STEMI, stroke, "
                    "airway, shock, anaphylaxis, trauma) else 'complex'. "
                    "Output ONLY one word."
                )
            ),
            HumanMessage(content=q),
        ]
    )
    label = (reply.content or "").strip().lower()
    route: Literal["emergency", "complex"] = (
        "emergency" if "emerg" in label else "complex"
    )
    log.info("classifier %r -> %s", q[:60], route)
    return {"route": route}


def retrieve(state: AssistantState) -> AssistantState:
    docs = retriever(k=4).invoke(state["question"])
    lines: list[str] = []
    citations: list[dict] = []
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("source", "unknown")
        page = d.metadata.get("page")
        label = f"{src}" + (f" p.{page}" if page else "")
        lines.append(f"[{i}] ({label})\n{d.page_content}")
        citations.append({"id": i, "source": src, "page": page})
    return {"context": "\n\n".join(lines), "citations": citations}


def _run(llm: ChatBedrockConverse, question: str, context: str) -> str:
    user = (
        f"Retrieved context:\n{context}\n\n"
        f"Clinician question: {question}\n"
        "Answer using only the context; cite with [1], [2] etc."
    )
    out = llm.invoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user)]
    )
    return out.content if isinstance(out.content, str) else str(out.content)


def answer_fast(state: AssistantState) -> AssistantState:
    return {"answer": _run(_fast, state["question"], state["context"])}


def answer_complex(state: AssistantState) -> AssistantState:
    return {"answer": _run(_teacher, state["question"], state["context"])}


def _route_next(state: AssistantState) -> Literal["answer_fast", "answer_complex"]:
    return "answer_fast" if state.get("route") == "emergency" else "answer_complex"


def build_graph():
    g = StateGraph(AssistantState)
    g.add_node("classify", classify)
    g.add_node("retrieve", retrieve)
    g.add_node("answer_fast", answer_fast)
    g.add_node("answer_complex", answer_complex)

    g.add_edge(START, "classify")
    g.add_edge("classify", "retrieve")
    g.add_conditional_edges("retrieve", _route_next, {
        "answer_fast": "answer_fast",
        "answer_complex": "answer_complex",
    })
    g.add_edge("answer_fast", END)
    g.add_edge("answer_complex", END)
    return g.compile()
