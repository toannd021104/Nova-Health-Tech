"""Router agent — picks the right department from a clinician's prompt.

Runs on **Qwen3 32B dense** on Bedrock Sydney (`qwen.qwen3-32b`). Qwen3-32B
is cheap ($0.1545 in / $0.6180 out per 1M tokens) and handles structured
JSON output well. Returns a RouterDecision so the LangGraph node can route
deterministically.
"""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any

import boto3

from poc.aws_qwen.app.agents import DEPARTMENTS, QWEN_ROUTER

log = logging.getLogger(__name__)

# Qwen on Bedrock lives in Sydney; the rest of the stack is Singapore.
BEDROCK_REGION = os.environ.get("BEDROCK_QWEN_REGION", "ap-southeast-2")

_ROUTER_SYSTEM = """You are a triage router for a clinical AI assistant. Given a clinician's question plus any short summary of attached artifacts (images, labs, notes), pick the single most appropriate clinical department from this list:

{departments}

Output exactly this JSON and nothing else:
{{"department": "<label>", "secondary": ["<label>", ...], "confidence": <0.0..1.0>, "reason": "<one short sentence>"}}

Rules:
- `department` is the primary owner. Pick the narrowest correct specialty.
- `secondary` is a list (possibly empty) of departments that must be consulted as a side-channel — e.g. include "infectious-disease" for any antibiotic question even if the primary is another specialty.
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
        # Qwen occasionally emits trailing whitespace or a fenced block — strip
        # both and extract the first JSON object.
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
    """Classify a question into a department via Qwen3-32B on Bedrock Converse."""
    bedrock = bedrock or boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

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
        modelId=QWEN_ROUTER,
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
