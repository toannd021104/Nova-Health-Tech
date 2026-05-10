"""LangGraph state machine for the POC.

Flow:

    incoming request
         │
         ▼
    PHI regex mask
         │
         ▼
    lane = emergency if state["emergency"] else "complex"  (pure if/else)
         │                │
         │ emergency       │ complex
         │ (Haiku 4.5)     │
         │                 ▼
         │          department router (Nova Micro)
         │                 │
         │                 ▼
         │          department-specific agent (Sonnet 4.5, Sonnet-vision if Radiology)
         │                 │
         ▼                 ▼
          RAG retrieve from FAISS (filtered by department namespace)
                   │
                   ▼
          generate grounded answer with inline [N] citations
                   │
                   ▼
          optional secondary-agent side channel (e.g. Clinical Pharmacy)
                   │
                   ▼
          guardrail + citation check → streaming SSE back
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

import boto3
from langgraph.graph import END, StateGraph

from poc.app.agents import DEPARTMENTS, Department, HAIKU
from poc.app.router import RouterDecision, route as route_department

log = logging.getLogger(__name__)


# Very small demo PHI pattern — production uses Comprehend Medical DetectPHI.
_PHI_PATTERNS = [
    (re.compile(r"\bMRN[:\s]*\d{4,12}\b", re.I), "[MRN]"),
    (re.compile(r"\bDOB[:\s]*\d{4}[-/]\d{1,2}[-/]\d{1,2}\b", re.I), "[DOB]"),
    (re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"), "[NAME]"),  # crude; flags "John Doe"
    (re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE]"),
]


def phi_mask(text: str) -> str:
    out = text
    for pattern, token in _PHI_PATTERNS:
        out = pattern.sub(token, out)
    return out


@dataclass
class ChatState:
    question: str
    emergency: bool = False
    attachments: list[dict[str, Any]] = field(default_factory=list)
    # populated during the graph
    masked_question: str = ""
    lane: str = ""            # "emergency" | "complex"
    router_decision: Optional[RouterDecision] = None
    department: Optional[Department] = None
    retrieved: list[dict[str, Any]] = field(default_factory=list)
    answer: str = ""
    citations: list[dict[str, Any]] = field(default_factory=list)
    route_badge: str = ""     # what the UI shows


def _node_phi_mask(state: ChatState) -> ChatState:
    state.masked_question = phi_mask(state.question)
    return state


def _node_pick_lane(state: ChatState) -> ChatState:
    state.lane = "emergency" if state.emergency else "complex"
    log.info("lane=%s (emergency=%s)", state.lane, state.emergency)
    return state


def _node_route_department(state: ChatState) -> ChatState:
    """Only called on the complex lane."""
    # If an image is attached, force radiology — matches the vision-agent rule.
    has_image = any(a.get("type", "").startswith("image/") for a in state.attachments)
    if has_image:
        state.department = DEPARTMENTS["radiology"]
        state.router_decision = RouterDecision(
            department="radiology",
            secondary=[],
            confidence=1.0,
            reason="image attached — forced to radiology",
        )
        state.route_badge = "Diagnostic Radiology (image)"
        return state

    decision = route_department(state.masked_question)
    state.router_decision = decision
    state.department = DEPARTMENTS.get(decision.department)
    if state.department is None:
        # General Medicine fallback — use Infectious Disease as a stand-in for
        # the POC since we didn't ship a dedicated GP agent.
        log.warning("router confidence too low or unknown dept; using pulmonology as fallback")
        state.department = DEPARTMENTS["pulmonology"]
        state.route_badge = f"General (routed via triage, confidence={decision.confidence:.2f})"
    else:
        state.route_badge = state.department.english
    return state


def _node_emergency_agent(state: ChatState) -> ChatState:
    """Emergency lane — bypass router, go straight to Haiku 4.5."""
    state.department = DEPARTMENTS["emergency"]
    state.route_badge = "Emergency Medicine"
    # Retrieval + generation happens in the next nodes, same as the complex
    # lane, but bounded to the emergency KB namespace.
    return state


def _node_retrieve(state: ChatState) -> ChatState:
    from poc.app.rag import retrieve  # lazy import so tests can stub it

    assert state.department is not None
    state.retrieved = retrieve(
        query=state.masked_question,
        namespace=state.department.kb_namespace,
        top_k=5,
    )
    state.citations = [
        {
            "id": i + 1,
            "source": chunk["source"],
            "page": chunk.get("page"),
            "snippet": chunk["text"][:300],
        }
        for i, chunk in enumerate(state.retrieved)
    ]
    return state


def _node_generate(state: ChatState, *, bedrock=None) -> ChatState:
    assert state.department is not None
    bedrock = bedrock or boto3.client("bedrock-runtime")

    # Build the context block with [N] tags matching citations.
    context_block = "\n\n".join(
        f"[{i + 1}] (source: {c['source']}, page: {c.get('page', 'n/a')})\n{c['text']}"
        for i, c in enumerate(state.retrieved)
    ) or "(no context retrieved — refuse to answer if the question needs grounding)"

    user_message = (
        f"Clinical context:\n{context_block}\n\n"
        f"Question:\n{state.masked_question}"
    )

    # Emergency lane forces Haiku 4.5 regardless of department default.
    model_id = HAIKU if state.lane == "emergency" else state.department.model
    max_tokens = 700 if state.lane == "emergency" else 1500
    temperature = 0.1 if state.lane == "emergency" else 0.2

    response = bedrock.converse(
        modelId=model_id,
        system=[{"text": state.department.system_prompt}],
        messages=[{"role": "user", "content": [{"text": user_message}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
    )
    state.answer = _extract_text(response)
    return state


def _extract_text(response: dict[str, Any]) -> str:
    parts = response.get("output", {}).get("message", {}).get("content", [])
    for p in parts:
        if "text" in p:
            return p["text"]
    return ""


def _branch_on_lane(state: ChatState) -> str:
    return "emergency" if state.lane == "emergency" else "complex"


def build_graph():
    """Build and compile the LangGraph state machine."""
    g: StateGraph = StateGraph(ChatState)
    g.add_node("phi_mask", _node_phi_mask)
    g.add_node("pick_lane", _node_pick_lane)
    g.add_node("emergency_agent", _node_emergency_agent)
    g.add_node("route_department", _node_route_department)
    g.add_node("retrieve", _node_retrieve)
    g.add_node("generate", _node_generate)

    g.set_entry_point("phi_mask")
    g.add_edge("phi_mask", "pick_lane")
    g.add_conditional_edges(
        "pick_lane",
        _branch_on_lane,
        {"emergency": "emergency_agent", "complex": "route_department"},
    )
    g.add_edge("emergency_agent", "retrieve")
    g.add_edge("route_department", "retrieve")
    g.add_edge("retrieve", "generate")
    g.add_edge("generate", END)
    return g.compile()
