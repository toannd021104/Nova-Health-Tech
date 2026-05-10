"""Router agent — picks the right department from a clinician's prompt.

Runs on Nova Micro for cost (~$0.00015 per call). Returns a structured JSON
decision so the LangGraph node can route deterministically.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

import boto3

from poc.app.agents import DEPARTMENTS, NOVA_MICRO

log = logging.getLogger(__name__)

_ROUTER_SYSTEM = """You are a triage router for a clinical AI assistant. Given a clinician's question plus any short summary of attached artifacts (images, labs, notes), pick the single most appropriate clinical department from this list:

{departments}

Output exactly this JSON and nothing else:
{{"department": "<label>", "secondary": ["<label>", ...], "confidence": <0.0..1.0>, "reason": "<one short sentence>"}}

Rules:
- `department` is the primary owner. Pick the narrowest correct specialty.
- `secondary` is a list (possibly empty) of departments that must be consulted as a side-channel — e.g. include "infectious-disease" for any antibiotic question even if the primary is another specialty; include "clinical-pharmacy" for any question with 2+ drugs.
- Never pick "emergency" here — emergency cases come in with a hard toggle flag and skip this router entirely. If the question looks time-critical, pick the most relevant non-emergency department AND set `reason` to note the urgency.
- If the question is imaging-centric or the user attached an image, pick "radiology".
- `confidence` < 0.6 means "I'm guessing" — the caller will fall back to general-medicine.
"""


@dataclass
class RouterDecision:
    department: str
    secondary: list[str]
    confidence: float
    reason: str

    @classmethod
    def from_llm_output(cls, raw: str) -> "RouterDecision":
        # Nova sometimes wraps JSON in code fences; strip them if present.
        raw = raw.strip()
        fence = re.search(r"\{[\s\S]*\}", raw)
        if not fence:
            raise ValueError(f"router LLM returned non-JSON: {raw!r}")
        obj = json.loads(fence.group(0))
        dept = obj.get("department", "general-medicine")
        if dept not in DEPARTMENTS and dept != "general-medicine":
            log.warning("router returned unknown dept %r; falling back", dept)
            dept = "general-medicine"
        return cls(
            department=dept,
            secondary=[d for d in obj.get("secondary", []) if d in DEPARTMENTS],
            confidence=float(obj.get("confidence", 0.0)),
            reason=obj.get("reason", ""),
        )


def route(question: str, attachments_summary: str = "", *, bedrock=None) -> RouterDecision:
    """Classify a question into a department via Nova Micro on Bedrock Converse."""
    bedrock = bedrock or boto3.client("bedrock-runtime")

    dept_list = "\n".join(
        f"- {d.label}: {d.english} ({d.vietnamese})"
        for d in DEPARTMENTS.values()
        if d.label != "emergency"  # emergency never gets routed here
    )
    system_prompt = _ROUTER_SYSTEM.format(departments=dept_list)

    user_content = [{"text": f"Question: {question}"}]
    if attachments_summary:
        user_content.append({"text": f"Attachments: {attachments_summary}"})

    response = bedrock.converse(
        modelId=NOVA_MICRO,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": user_content}],
        inferenceConfig={"maxTokens": 200, "temperature": 0.0},
    )

    raw_text = _extract_text(response)
    try:
        return RouterDecision.from_llm_output(raw_text)
    except Exception as exc:  # noqa: BLE001
        log.error("router parsing failed: %s; raw=%r", exc, raw_text)
        return RouterDecision(
            department="general-medicine",
            secondary=[],
            confidence=0.0,
            reason=f"router-fallback: {exc}",
        )


def _extract_text(response: dict[str, Any]) -> str:
    parts = response.get("output", {}).get("message", {}).get("content", [])
    for p in parts:
        if "text" in p:
            return p["text"]
    return ""
