"""FastAPI POC server.

Run locally:
    uvicorn poc.aws_qwen.app.server:app --reload --port 8000

Deploy as Lambda: wrapped by Mangum in the SAM template.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from poc.aws_qwen.app.graph import ChatState, build_graph

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
log = logging.getLogger("poc.server")

app = FastAPI(title="Nova Health POC")

# Static UI — mounted at /ui, the Lambda router forwards /ui/* here.
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    app.mount("/ui", StaticFiles(directory=_static_dir, html=True), name="ui")

# Compile the graph once per container.
_GRAPH = build_graph()

# Single-tenant access token — simple enough for a 10-day demo. Overridable
# via environment variable set by poc/deploy.py.
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
        return  # local dev without auth
    token = request.query_params.get("token") or request.headers.get("x-poc-token", "")
    if token != POC_ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="bad or missing token")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request) -> dict[str, Any]:
    _check_token(request)

    state = ChatState(
        question=req.message,
        emergency=req.emergency,
        attachments=[a.model_dump() for a in req.attachments],
    )

    # Run the graph synchronously inside a threadpool so boto3 doesn't block
    # the event loop.
    loop = asyncio.get_running_loop()
    final = await loop.run_in_executor(None, _GRAPH.invoke, state)

    return {
        "route": {
            "lane": final.lane,
            "badge": final.route_badge,
            "department": final.department.label if final.department else None,
            "confidence": final.router_decision.confidence if final.router_decision else None,
            "reason": final.router_decision.reason if final.router_decision else None,
        },
        "answer": final.answer,
        "citations": final.citations,
    }


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    # Redirect to the UI bundle when hitting the root.
    return HTMLResponse(
        '<!doctype html><meta http-equiv="refresh" content="0; url=/ui/index.html">'
    )
