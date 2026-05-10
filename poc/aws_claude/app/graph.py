"""LangGraph state machine for the POC (Version A — AWS + Claude, non-fine-tuned).

Flow:

    incoming request
         │
         ▼
    PHI regex mask
         │
         ▼
    Redis semantic-cache lookup (Layer 1)
         │ hit → return cached answer, skip LLM
         │ miss
         ▼
    lane = emergency if state["emergency"] else "complex"  (pure if/else)
         │                 │
         │ emergency        │ complex
         │ Claude Haiku 4.5 │
         │                  ▼
         │           department router (Nova Micro)
         │                  │
         │                  ▼
         │           department-specific agent (Claude Sonnet 4.5;
         │                                       vision for Radiology)
         │                  │
         ▼                  ▼
          Hybrid RAG retrieve (FAISS top-20 → Amazon Rerank top-5)
                   │
                   ▼
          Optional GraphRAG tool (`graph_retrieve`) on multi-hop questions
                   │
                   ▼
          Generate grounded answer with inline [N] citations
                   (Bedrock Prompt Caching is enabled by Claude 4.x automatically
                    on the static prefix — no cachePoint marker needed)
                   │
                   ▼
          Write-back to Redis cache (TTL 10 min emergency, 24 hr complex)
                   │
                   ▼
          Streaming SSE back to the browser

Everything runs in ap-southeast-1 except the Amazon Rerank call (Tokyo).
No fine-tuning in this POC — base Claude only.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

import boto3
from langgraph.graph import END, StateGraph

from poc.aws_claude.app import cache as redis_cache
from poc.aws_claude.app import graphrag
from poc.aws_claude.app.agents import DEPARTMENTS, CLAUDE_HAIKU, Department
from poc.aws_claude.app.router import BEDROCK_REGION, RouterDecision, route as route_department

log = logging.getLogger(__name__)


# Very small demo PHI pattern — production uses Comprehend Medical DetectPHI.
_PHI_PATTERNS = [
    (re.compile(r"\bMRN[:\s]*\d{4,12}\b", re.I), "[MRN]"),
    (re.compile(r"\bDOB[:\s]*\d{4}[-/]\d{1,2}[-/]\d{1,2}\b", re.I), "[DOB]"),
    (re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"), "[NAME]"),
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
    masked_question: str = ""
    lane: str = ""
    router_decision: Optional[RouterDecision] = None
    department: Optional[Department] = None
    retrieved: list[dict[str, Any]] = field(default_factory=list)
    graph_hits: list[dict[str, Any]] = field(default_factory=list)
    answer: str = ""
    citations: list[dict[str, Any]] = field(default_factory=list)
    route_badge: str = ""
    cache_hit: bool = False


def _node_phi_mask(state: ChatState) -> ChatState:
    state.masked_question = phi_mask(state.question)
    return state


def _node_pick_lane(state: ChatState) -> ChatState:
    state.lane = "emergency" if state.emergency else "complex"
    log.info("lane=%s (emergency=%s)", state.lane, state.emergency)
    return state


def _node_cache_lookup(state: ChatState) -> ChatState:
    if state.lane != "emergency":
        return state
    hit = redis_cache.get(
        question=state.masked_question,
        department="emergency",
        emergency=True,
    )
    if hit is None:
        return state
    log.info("cache hit on emergency lane")
    state.cache_hit = True
    state.answer = hit.answer
    state.citations = hit.citations
    state.route_badge = hit.route_badge or "Emergency Medicine (cached)"
    state.department = DEPARTMENTS["emergency"]
    return state


def _node_route_department(state: ChatState) -> ChatState:
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
        log.warning("router fallback -> pulmonology")
        state.department = DEPARTMENTS["pulmonology"]
        state.route_badge = (
            f"General (routed via triage, confidence={decision.confidence:.2f})"
        )
    else:
        state.route_badge = state.department.english

    hit = redis_cache.get(
        question=state.masked_question,
        department=state.department.label,
        emergency=False,
    )
    if hit is not None:
        log.info("cache hit on complex lane / %s", state.department.label)
        state.cache_hit = True
        state.answer = hit.answer
        state.citations = hit.citations
        state.route_badge = hit.route_badge or state.department.english + " (cached)"
    return state


def _node_emergency_agent(state: ChatState) -> ChatState:
    if state.cache_hit:
        return state
    state.department = DEPARTMENTS["emergency"]
    state.route_badge = "Emergency Medicine"
    return state


def _node_retrieve(state: ChatState) -> ChatState:
    if state.cache_hit:
        return state
    from poc.aws_claude.app.rag import retrieve  # lazy import so tests can stub

    assert state.department is not None
    state.retrieved = retrieve(
        query=state.masked_question,
        namespace=state.department.kb_namespace,
        top_k=5,
    )

    if (
        state.lane == "complex"
        and (" and " in state.masked_question.lower() or "," in state.masked_question)
    ):
        graph_hits = graphrag.graph_retrieve(state.masked_question, top_k=3)
        state.graph_hits = [
            {"source": h.source, "text": h.text, "score": h.score} for h in graph_hits
        ]

    state.citations = [
        {
            "id": i + 1,
            "source": chunk["source"],
            "page": chunk.get("page"),
            "snippet": chunk["text"][:300],
            "origin": "vector",
        }
        for i, chunk in enumerate(state.retrieved)
    ]
    for i, chunk in enumerate(state.graph_hits, start=len(state.citations) + 1):
        state.citations.append(
            {
                "id": i,
                "source": chunk["source"],
                "page": None,
                "snippet": chunk["text"][:300],
                "origin": "graph",
            }
        )
    return state


def _node_generate(state: ChatState, *, bedrock=None) -> ChatState:
    if state.cache_hit:
        return state
    assert state.department is not None
    bedrock = bedrock or boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

    context_parts = []
    for c in state.citations:
        origin = c.get("origin", "vector")
        page = f", page: {c.get('page', 'n/a')}" if c.get("page") else ""
        context_parts.append(
            f"[{c['id']}] (source: {c['source']}{page}, origin: {origin})\n{c['snippet']}"
        )
    context_block = "\n\n".join(context_parts) or (
        "(no context retrieved — refuse to answer if the question needs grounding)"
    )

    user_message = (
        f"Clinical context:\n{context_block}\n\n"
        f"Question:\n{state.masked_question}"
    )

    # Emergency forces Haiku 4.5 regardless of department default.
    model_id = CLAUDE_HAIKU if state.lane == "emergency" else state.department.model
    max_tokens = 700 if state.lane == "emergency" else 1500
    # Claude rejects sending both temperature and top_p; use temperature only.
    temperature = 0.1 if state.lane == "emergency" else 0.2

    user_content: list[dict[str, Any]] = [{"text": user_message}]
    if state.department.label == "radiology":
        for att in state.attachments:
            mime = att.get("type", "")
            if mime.startswith("image/"):
                import base64  # noqa: PLC0415

                raw = base64.b64decode(att.get("data_b64", ""))
                user_content.append(
                    {
                        "image": {
                            "format": mime.split("/")[-1],
                            "source": {"bytes": raw},
                        }
                    }
                )

    response = bedrock.converse(
        modelId=model_id,
        system=[{"text": state.department.system_prompt}],
        messages=[{"role": "user", "content": user_content}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
    )
    state.answer = _extract_text(response)
    return state


def _node_cache_write(state: ChatState) -> ChatState:
    if state.cache_hit or not state.answer or state.department is None:
        return state
    redis_cache.put(
        question=state.masked_question,
        department=state.department.label,
        emergency=state.emergency,
        answer=state.answer,
        citations=state.citations,
        route_badge=state.route_badge,
    )
    return state


def _extract_text(response: dict[str, Any]) -> str:
    parts = response.get("output", {}).get("message", {}).get("content", [])
    for p in parts:
        if "text" in p:
            return p["text"]
    return ""


def _branch_on_lane(state: ChatState) -> str:
    if state.cache_hit:
        return "cached"
    return "emergency" if state.lane == "emergency" else "complex"


def build_graph():
    g: StateGraph = StateGraph(ChatState)
    g.add_node("phi_mask", _node_phi_mask)
    g.add_node("pick_lane", _node_pick_lane)
    g.add_node("cache_lookup", _node_cache_lookup)
    g.add_node("emergency_agent", _node_emergency_agent)
    g.add_node("route_department", _node_route_department)
    g.add_node("retrieve", _node_retrieve)
    g.add_node("generate", _node_generate)
    g.add_node("cache_write", _node_cache_write)

    g.set_entry_point("phi_mask")
    g.add_edge("phi_mask", "pick_lane")
    g.add_edge("pick_lane", "cache_lookup")
    g.add_conditional_edges(
        "cache_lookup",
        _branch_on_lane,
        {
            "emergency": "emergency_agent",
            "complex": "route_department",
            "cached": "cache_write",
        },
    )
    g.add_edge("emergency_agent", "retrieve")
    g.add_edge("route_department", "retrieve")
    g.add_edge("retrieve", "generate")
    g.add_edge("generate", "cache_write")
    g.add_edge("cache_write", END)
    return g.compile()
