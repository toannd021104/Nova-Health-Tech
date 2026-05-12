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
from fastapi.responses import HTMLResponse
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
