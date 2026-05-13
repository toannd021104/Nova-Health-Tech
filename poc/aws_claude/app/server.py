"""FastAPI PoC server (Version A — AWS + Claude).

On a fresh EC2 boot, the first `/healthz` call (or the server startup event)
bootstraps the FAISS indexes from the S3 bucket populated by deploy.py. Once
bootstrap is complete, /api/chat runs the full LangGraph: PHI mask -> cache
-> emergency/complex lane -> router -> retrieve -> generate -> cache-write.

Run locally:
    uvicorn poc.aws_claude.app.server:app --reload --port 8000

On the EC2 (via setup_instance.py):
    uvicorn app.server:app --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from .graph import ChatState, build_graph
    from . import rag as rag_module
except ImportError:  # pragma: no cover
    from app.graph import ChatState, build_graph  # type: ignore
    from app import rag as rag_module  # type: ignore

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("poc.aws_claude.server")


_GRAPH = None
_BOOTSTRAP_STATS: dict[str, Any] = {"state": "pending"}


def get_graph():
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = build_graph()
    return _GRAPH


def _do_bootstrap() -> None:
    """Build FAISS namespaces from S3 if not already present."""
    global _BOOTSTRAP_STATS
    try:
        _BOOTSTRAP_STATS = {"state": "running"}
        stats = rag_module.bootstrap_from_s3()
        _BOOTSTRAP_STATS = {"state": "ready", **stats}
    except Exception as exc:  # noqa: BLE001
        _BOOTSTRAP_STATS = {"state": "error", "error": str(exc)}
        log.exception("FAISS bootstrap failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bedrock KB handles indexing — no local FAISS bootstrap needed.
    # Just mark ready immediately.
    global _BOOTSTRAP_STATS
    _BOOTSTRAP_STATS = {"state": "ready", "kb_id": os.environ.get("BEDROCK_KB_ID", "MUEEBGPRSJ")}
    yield


app = FastAPI(title="Nova Health PoC — AWS + Claude", lifespan=lifespan)

# Static UI. In local dev the folder is poc/aws_claude/app/static/.
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    app.mount("/ui", StaticFiles(directory=_static_dir, html=True), name="ui")


POC_ACCESS_TOKEN = os.environ.get("POC_ACCESS_TOKEN", "")


class Attachment(BaseModel):
    type: str = Field(..., description="MIME type, e.g. image/png")
    name: str
    data_b64: str


class ChatRequest(BaseModel):
    message: str
    emergency: bool = False
    attachments: list[Attachment] = Field(default_factory=list)


def _check_token(request: Request) -> None:
    if not POC_ACCESS_TOKEN:
        return
    token = request.query_params.get("token") or request.headers.get("x-poc-token", "")
    if token != POC_ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="bad or missing token")


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    return {
        "status": "ok",
        "bootstrap": _BOOTSTRAP_STATS,
        "region": os.environ.get("AWS_REGION", "ap-southeast-1"),
        "bucket": os.environ.get("S3_BUCKET", ""),
    }


@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request) -> dict[str, Any]:
    _check_token(request)
    if _BOOTSTRAP_STATS.get("state") not in ("ready", "pending"):
        # "running" is accepted — retrieve will just raise FileNotFoundError
        # and surface a clear message; "error" blocks.
        if _BOOTSTRAP_STATS.get("state") == "error":
            raise HTTPException(
                status_code=503,
                detail=f"bootstrap failed: {_BOOTSTRAP_STATS.get('error')}",
            )

    state = ChatState(
        question=req.message,
        emergency=req.emergency,
        attachments=[a.model_dump() for a in req.attachments],
    )

    loop = asyncio.get_running_loop()
    final = await loop.run_in_executor(None, get_graph().invoke, state)

    # LangGraph may return AddableValuesDict or ChatState depending on version
    def _get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    route_info = _get(final, "route_badge", "")
    lane = _get(final, "lane", "")
    dept = _get(final, "department", None)
    router_dec = _get(final, "router_decision", None)

    return {
        "route": {
            "lane": lane,
            "badge": route_info,
            "department": dept.label if dept and hasattr(dept, "label") else (dept.get("label") if isinstance(dept, dict) else None),
            "confidence": router_dec.confidence if router_dec and hasattr(router_dec, "confidence") else None,
            "reason": router_dec.reason if router_dec and hasattr(router_dec, "reason") else None,
        },
        "answer": _get(final, "answer", ""),
        "citations": _get(final, "citations", []),
    }


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(
        '<!doctype html><meta http-equiv="refresh" content="0; url=/ui/index.html">'
    )


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest, request: Request):
    """Streaming SSE endpoint — sends tokens as they arrive from Bedrock.

    Returns Server-Sent Events:
      event: route   data: {"lane": ..., "department": ...}
      event: token   data: {"text": "..."}
      event: done    data: {"citations": [...]}
    """
    import json as _json

    _check_token(request)

    state = ChatState(
        question=req.message,
        emergency=req.emergency,
        attachments=[a.model_dump() for a in req.attachments],
    )

    import time as _time

    loop = asyncio.get_running_loop()

    # Run graph up to generate (phi_mask, pick_lane, cache_lookup, route, retrieve)
    # Then stream the generate step
    def _run_pre_generate():
        graph = get_graph()
        from app.graph import (
            _node_phi_mask, _node_pick_lane, _node_cache_lookup,
            _branch_on_lane, _node_emergency_agent, _node_route_department,
            _node_retrieve,
        )
        t_start = _time.time()
        state_out = _node_phi_mask(state)
        state_out = _node_pick_lane(state_out)
        state_out = _node_cache_lookup(state_out)
        branch = _branch_on_lane(state_out)
        if branch == "cached":
            state_out._pre_gen_ms = int((_time.time() - t_start) * 1000)
            return state_out
        elif branch == "emergency":
            state_out = _node_emergency_agent(state_out)
        else:
            state_out = _node_route_department(state_out)
        if state_out.cache_hit:
            state_out._pre_gen_ms = int((_time.time() - t_start) * 1000)
            return state_out
        t_retrieve = _time.time()
        state_out = _node_retrieve(state_out)
        state_out._retrieve_ms = int((_time.time() - t_retrieve) * 1000)
        state_out._pre_gen_ms = int((_time.time() - t_start) * 1000)
        return state_out

    pre_state = await loop.run_in_executor(None, _run_pre_generate)

    def _get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    async def event_generator():
        # Send route info first (includes pre-generate timing)
        dept = pre_state.department
        pre_gen_ms = getattr(pre_state, '_pre_gen_ms', 0)
        retrieve_ms = getattr(pre_state, '_retrieve_ms', 0)
        route_data = {
            "lane": pre_state.lane,
            "badge": pre_state.route_badge,
            "department": dept.label if dept else None,
            "preGenMs": pre_gen_ms,
            "retrieveMs": retrieve_ms,
        }
        yield f"event: route\ndata: {_json.dumps(route_data)}\n\n"

        # If cached, send full answer immediately
        if pre_state.cache_hit:
            yield f"event: token\ndata: {_json.dumps({'text': pre_state.answer})}\n\n"
            yield f"event: done\ndata: {_json.dumps({'citations': pre_state.citations})}\n\n"
            return

        # Stream generate via converse_stream
        import boto3 as _boto3
        from app.graph import BEDROCK_REGION
        from app.agents import CLAUDE_HAIKU

        bedrock = _boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

        context_parts = []
        for c in pre_state.citations:
            origin = c.get("origin", "vector")
            page = f", page: {c.get('page', 'n/a')}" if c.get("page") else ""
            context_parts.append(
                f"[{c['id']}] (source: {c['source']}{page}, origin: {origin})\n{c['snippet']}"
            )
        context_block = "\n\n".join(context_parts) or (
            "(no context retrieved)"
        )

        user_message = f"Clinical context:\n{context_block}\n\nQuestion:\n{pre_state.masked_question}"
        model_id = CLAUDE_HAIKU if pre_state.lane == "emergency" else (dept.model if dept else CLAUDE_HAIKU)
        # Emergency: 300 tokens max for speed. Complex: 1500 for thorough answers.
        max_tokens = 300 if pre_state.lane == "emergency" else 1500
        temperature = 0.1 if pre_state.lane == "emergency" else 0.2

        guardrail_id = os.environ.get("GUARDRAIL_ID", "azsgfl02i9gn")
        converse_kwargs = dict(
            modelId=model_id,
            system=[{"text": dept.system_prompt if dept else "You are a clinical assistant."}],
            messages=[{"role": "user", "content": [{"text": user_message}]}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
        )
        # Emergency lane: NO guardrails (speed priority, check post-hoc if needed)
        # Complex lane: guardrails enabled
        if guardrail_id and pre_state.lane != "emergency":
            converse_kwargs["guardrailConfig"] = {
                "guardrailIdentifier": guardrail_id,
                "guardrailVersion": "DRAFT",
                "trace": "enabled",
            }

        input_tokens = 0
        output_tokens = 0
        try:
            resp = bedrock.converse_stream(**converse_kwargs)
            for event in resp.get("stream", []):
                if "contentBlockDelta" in event:
                    delta = event["contentBlockDelta"].get("delta", {})
                    text = delta.get("text", "")
                    if text:
                        yield f"event: token\ndata: {_json.dumps({'text': text})}\n\n"
                elif "metadata" in event:
                    usage = event["metadata"].get("usage", {})
                    input_tokens = usage.get("inputTokens", 0)
                    output_tokens = usage.get("outputTokens", 0)
        except Exception as e:
            yield f"event: error\ndata: {_json.dumps({'error': str(e)})}\n\n"

        yield f"event: done\ndata: {_json.dumps({'citations': pre_state.citations, 'usage': {'inputTokens': input_tokens, 'outputTokens': output_tokens}})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
