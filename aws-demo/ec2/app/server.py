"""FastAPI server exposing /api/chat and optional EntraID OIDC login.

EntraID auth is disabled by default (ENTRA_ENABLED=false). Setting it to true
requires adding `http(s)://<host>/api/auth/callback` as a redirect URI in the
Azure app registration first.
"""
from __future__ import annotations

import logging
import os
import secrets
import time
from pathlib import Path

from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from graph import build_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("server")

app = FastAPI(title="Nova Clinical GenAI (demo)")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET", secrets.token_urlsafe(32)),
    same_site="lax",
    https_only=False,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph = None


def graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


# ── OIDC (EntraID) — optional ────────────────────────────────────────────
_entra_enabled = os.environ.get("ENTRA_ENABLED", "false").lower() == "true"
oauth = OAuth()
if _entra_enabled:
    tenant = os.environ["ENTRA_TENANT_ID"]
    oauth.register(
        "entra",
        client_id=os.environ["ENTRA_CLIENT_ID"],
        client_secret=os.environ["ENTRA_CLIENT_SECRET"],
        server_metadata_url=(
            f"https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration"
        ),
        client_kwargs={"scope": "openid profile email"},
    )


def _require_user_if_enabled(request: Request) -> dict | None:
    if not _entra_enabled:
        return {"name": "demo", "upn": "demo@nova.local"}
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="login required")
    return user


@app.get("/api/health")
def health():
    # kick the graph once so FAISS is warm
    try:
        graph()
        return {"status": "ok"}
    except Exception as exc:
        log.exception("health failed")
        return JSONResponse({"status": "error", "detail": str(exc)}, status_code=500)


@app.get("/api/me")
def me(request: Request):
    return _require_user_if_enabled(request) or {"name": "demo", "upn": "demo@nova.local"}


@app.get("/api/auth/login")
async def login(request: Request):
    if not _entra_enabled:
        raise HTTPException(status_code=404, detail="auth disabled")
    redirect_uri = request.url_for("auth_callback")
    return await oauth.entra.authorize_redirect(request, str(redirect_uri))


@app.get("/api/auth/callback", name="auth_callback")
async def auth_callback(request: Request):
    if not _entra_enabled:
        raise HTTPException(status_code=404, detail="auth disabled")
    token = await oauth.entra.authorize_access_token(request)
    claims = token.get("userinfo") or {}
    request.session["user"] = {
        "name": claims.get("name"),
        "upn": claims.get("preferred_username") or claims.get("email"),
        "sub": claims.get("sub"),
    }
    return RedirectResponse(url="/")


@app.get("/api/auth/logout")
def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")


class ChatReq(BaseModel):
    message: str


@app.post("/api/chat")
def chat(req: ChatReq, request: Request):
    _require_user_if_enabled(request)
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="message required")

    t0 = time.time()
    result = graph().invoke({"question": req.message.strip()})
    dur_ms = int((time.time() - t0) * 1000)

    return {
        "answer": result.get("answer") or "(no answer)",
        "route": result.get("route"),
        "citations": result.get("citations") or [],
        "latency_ms": dur_ms,
        "model": (
            os.environ.get("BEDROCK_MODEL_ID")
            if result.get("route") == "emergency"
            else os.environ.get("BEDROCK_TEACHER_MODEL_ID")
        ),
    }


# ── Static frontend ─────────────────────────────────────────────────────
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
