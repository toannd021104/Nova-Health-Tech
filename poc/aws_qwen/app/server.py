"""FastAPI PoC server (Version B — AWS + Qwen).

Run locally:
    uvicorn poc.aws_qwen.app.server:app --reload --port 8001

Features:
- /api/chat/stream  — SSE streaming (same pattern as aws_claude)
- /api/phi/scan     — show what PHI was masked
- /api/student/chat — route to fine-tuned student model if loaded
- /ui               — static chat UI
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
    from .graph import ChatState, build_graph, phi_mask, _PHI_PATTERNS
    from . import rag as rag_module
except ImportError:
    from app.graph import ChatState, build_graph, phi_mask, _PHI_PATTERNS  # type: ignore
    from app import rag as rag_module  # type: ignore

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("poc.aws_qwen.server")

_GRAPH = None
_BOOTSTRAP_STATS: dict[str, Any] = {"state": "pending"}
_BEDROCK_RT_CLIENT = None
_STUDENT_PIPELINE = None   # loaded lazily when first /api/student/chat is called


def _get_bedrock_client():
    global _BEDROCK_RT_CLIENT
    if _BEDROCK_RT_CLIENT is None:
        import boto3 as _boto3
        region = os.environ.get("AWS_REGION", "ap-southeast-1")
        _BEDROCK_RT_CLIENT = _boto3.client("bedrock-runtime", region_name=region)
    return _BEDROCK_RT_CLIENT


def get_graph():
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = build_graph()
    return _GRAPH


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _BOOTSTRAP_STATS
    _BOOTSTRAP_STATS = {"state": "ready", "note": "FAISS indexes loaded on first query"}
    yield


app = FastAPI(title="Nova Health PoC — AWS + Qwen", lifespan=lifespan)

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


class StudentChatRequest(BaseModel):
    message: str
    emergency: bool = False
    max_new_tokens: int = 512
    temperature: float = 0.2


def _check_token(request: Request) -> None:
    if not POC_ACCESS_TOKEN:
        return
    token = request.query_params.get("token") or request.headers.get("x-poc-token", "")
    if token != POC_ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="bad or missing token")


# ── PHI scan ──────────────────────────────────────────────────────────────────

@app.post("/api/phi/scan")
async def phi_scan(req: ChatRequest) -> dict[str, Any]:
    """Return original text, masked text, and list of detected PHI tokens."""
    import re as _re
    original = req.message
    masked = phi_mask(original)
    detected = []
    for pattern, token in _PHI_PATTERNS:
        for match in pattern.finditer(original):
            detected.append({
                "type": token.strip("[]"),
                "original_value": match.group(0),
                "replaced_with": token,
                "position": [match.start(), match.end()],
            })
    detected.sort(key=lambda x: x["position"][0])
    return {
        "original": original,
        "masked": masked,
        "phi_detected": original != masked,
        "phi_count": len(detected),
        "detections": detected,
    }


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/healthz")
def healthz() -> dict[str, Any]:
    student_loaded = _STUDENT_PIPELINE is not None
    student_path = os.environ.get("STUDENT_MODEL_PATH", "")
    student_endpoint = os.environ.get("STUDENT_ENDPOINT_NAME", "")
    return {
        "status": "ok",
        "bootstrap": _BOOTSTRAP_STATS,
        "student_loaded": student_loaded,
        "student_mode": "sagemaker" if student_endpoint else ("local" if student_path else "none"),
        "student_endpoint": student_endpoint or "not configured",
        "student_path": student_path or "not configured",
        "bedrock_region": os.environ.get("AWS_REGION", "ap-southeast-1"),
        "vector_kb": os.environ.get("BEDROCK_KB_ID", "MUEEBGPRSJ"),
        "graphrag_kb": os.environ.get("BEDROCK_GRAPHRAG_KB_ID", "FU6SXD0B8B"),
    }


# ── Non-streaming chat (kept for compatibility) ───────────────────────────────

@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request) -> dict[str, Any]:
    _check_token(request)
    state = ChatState(
        question=req.message,
        emergency=req.emergency,
        attachments=[a.model_dump() for a in req.attachments],
    )
    loop = asyncio.get_running_loop()
    final = await loop.run_in_executor(None, get_graph().invoke, state)

    def _get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    dept = _get(final, "department", None)
    router_dec = _get(final, "router_decision", None)
    return {
        "route": {
            "lane": _get(final, "lane", ""),
            "badge": _get(final, "route_badge", ""),
            "department": dept.label if dept and hasattr(dept, "label") else None,
            "confidence": router_dec.confidence if router_dec else None,
            "reason": router_dec.reason if router_dec else None,
        },
        "answer": _get(final, "answer", ""),
        "citations": _get(final, "citations", []),
    }


# ── Streaming chat ────────────────────────────────────────────────────────────

@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest, request: Request):
    """SSE streaming endpoint — mirrors aws_claude streaming pattern.

    Events:
      event: route   data: {lane, badge, department, preGenMs, retrieveMs}
      event: token   data: {text}
      event: done    data: {citations, usage}
      event: error   data: {error}
    """
    import json as _json
    import time as _time

    _check_token(request)

    state = ChatState(
        question=req.message,
        emergency=req.emergency,
        attachments=[a.model_dump() for a in req.attachments],
    )

    loop = asyncio.get_running_loop()

    def _run_pre_generate():
        try:
            from app.graph import (
                _node_phi_mask, _node_pick_lane, _node_cache_lookup,
                _branch_on_lane, _node_emergency_agent, _node_route_department,
                _node_retrieve,
            )
        except ImportError:
            from poc.aws_qwen.app.graph import (  # type: ignore
                _node_phi_mask, _node_pick_lane, _node_cache_lookup,
                _branch_on_lane, _node_emergency_agent, _node_route_department,
                _node_retrieve,
            )
        t0 = _time.time()
        s = _node_phi_mask(state)
        s = _node_pick_lane(s)
        s = _node_cache_lookup(s)
        branch = _branch_on_lane(s)
        if branch == "cached":
            s._pre_gen_ms = int((_time.time() - t0) * 1000)
            return s
        elif branch == "emergency":
            s = _node_emergency_agent(s)
        else:
            s = _node_route_department(s)
        if s.cache_hit:
            s._pre_gen_ms = int((_time.time() - t0) * 1000)
            return s
        t_ret = _time.time()
        s = _node_retrieve(s)
        s._retrieve_ms = int((_time.time() - t_ret) * 1000)
        s._pre_gen_ms = int((_time.time() - t0) * 1000)
        return s

    pre_state = await loop.run_in_executor(None, _run_pre_generate)

    async def event_generator():
        dept = pre_state.department
        pre_gen_ms = getattr(pre_state, "_pre_gen_ms", 0)
        retrieve_ms = getattr(pre_state, "_retrieve_ms", 0)
        route_data = {
            "lane": pre_state.lane,
            "badge": pre_state.route_badge,
            "department": dept.label if dept else None,
            "preGenMs": pre_gen_ms,
            "retrieveMs": retrieve_ms,
            "model": "teacher",   # flag: this is the teacher (Qwen Plus) path
        }
        yield f"event: route\ndata: {_json.dumps(route_data)}\n\n"

        if pre_state.cache_hit:
            yield f"event: token\ndata: {_json.dumps({'text': pre_state.answer})}\n\n"
            yield f"event: done\ndata: {_json.dumps({'citations': pre_state.citations})}\n\n"
            return

        # Build context block
        context_parts = []
        for c in pre_state.citations:
            origin = c.get("origin", "vector")
            page = f", page: {c.get('page', 'n/a')}" if c.get("page") else ""
            context_parts.append(
                f"[{c['id']}] (source: {c['source']}{page}, origin: {origin})\n{c['snippet']}"
            )
        context_block = "\n\n".join(context_parts) or "(no context retrieved)"

        user_message = f"Clinical context:\n{context_block}\n\nQuestion:\n{pre_state.masked_question}"

        try:
            from app.agents import NOVA_LITE
        except ImportError:
            from poc.aws_qwen.app.agents import NOVA_LITE  # type: ignore

        model_id = NOVA_LITE if pre_state.lane == "emergency" else (
            dept.model if dept else NOVA_LITE
        )
        max_tokens = 300 if pre_state.lane == "emergency" else 1500
        temperature = 0.1 if pre_state.lane == "emergency" else 0.2

        bedrock = _get_bedrock_client()
        converse_kwargs = dict(
            modelId=model_id,
            system=[{"text": dept.system_prompt if dept else "You are a clinical assistant."}],
            messages=[{"role": "user", "content": [{"text": user_message}]}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
        )

        queue: asyncio.Queue = asyncio.Queue()

        def _stream_worker():
            try:
                resp = bedrock.converse_stream(**converse_kwargs)
                for event in resp.get("stream", []):
                    if "contentBlockDelta" in event:
                        delta = event["contentBlockDelta"].get("delta", {})
                        text = delta.get("text", "")
                        if text:
                            queue.put_nowait(("token", text))
                    elif "metadata" in event:
                        queue.put_nowait(("metadata", event["metadata"].get("usage", {})))
            except Exception as e:
                queue.put_nowait(("error", str(e)))
            finally:
                queue.put_nowait(("done", None))

        loop.run_in_executor(None, _stream_worker)

        input_tokens = output_tokens = 0
        while True:
            msg = await queue.get()
            if msg[0] == "token":
                yield f"event: token\ndata: {_json.dumps({'text': msg[1]})}\n\n"
            elif msg[0] == "metadata":
                input_tokens = msg[1].get("inputTokens", 0)
                output_tokens = msg[1].get("outputTokens", 0)
            elif msg[0] == "error":
                yield f"event: error\ndata: {_json.dumps({'error': msg[1]})}\n\n"
                break
            elif msg[0] == "done":
                break

        yield f"event: done\ndata: {_json.dumps({'citations': pre_state.citations, 'usage': {'inputTokens': input_tokens, 'outputTokens': output_tokens}})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Student model inference ───────────────────────────────────────────────────

def _load_student():
    """Connect to the SageMaker Endpoint for student inference.

    The student model (Qwen3-4B + LoRA) is deployed as a SageMaker Endpoint
    (ml.g4dn.xlarge, T4 16GB) in ap-southeast-1.
    """
    global _STUDENT_PIPELINE
    if _STUDENT_PIPELINE is not None:
        return _STUDENT_PIPELINE

    endpoint_name = os.environ.get("STUDENT_ENDPOINT_NAME", "")
    model_path = os.environ.get("STUDENT_MODEL_PATH", "")

    if not endpoint_name and not model_path:
        raise HTTPException(
            status_code=503,
            detail="Set STUDENT_ENDPOINT_NAME (SageMaker) or STUDENT_MODEL_PATH (local).",
        )

    if endpoint_name:
        # SageMaker Endpoint mode — no local model loading needed
        log.info("Using SageMaker Endpoint: %s", endpoint_name)
        _STUDENT_PIPELINE = ("sagemaker", endpoint_name)
        return _STUDENT_PIPELINE

    # Local model fallback (needs enough disk/RAM)
    try:
        import torch  # noqa: PLC0415
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline as hf_pipeline  # noqa: PLC0415

        adapter_path = os.path.join(model_path, "adapter")
        if os.path.isdir(adapter_path) and os.path.exists(os.path.join(adapter_path, "adapter_config.json")):
            log.info("Loading student LoRA adapter from %s ...", adapter_path)
            import json as _json
            with open(os.path.join(adapter_path, "adapter_config.json")) as f:
                adapter_cfg = _json.load(f)
            base_model_name = adapter_cfg.get("base_model_name_or_path", "Qwen/Qwen3-4B")

            from peft import PeftModel  # noqa: PLC0415
            tokenizer = AutoTokenizer.from_pretrained(adapter_path, trust_remote_code=True)
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
                device_map="auto",
                trust_remote_code=True,
            )
            model = PeftModel.from_pretrained(base_model, adapter_path)
            model = model.merge_and_unload()
            _STUDENT_PIPELINE = hf_pipeline("text-generation", model=model, tokenizer=tokenizer)
        else:
            log.info("Loading merged student model from %s ...", model_path)
            _STUDENT_PIPELINE = hf_pipeline(
                "text-generation", model=model_path, device_map="auto",
                torch_dtype="auto", trust_remote_code=True,
            )
        log.info("Student model loaded locally.")
        return _STUDENT_PIPELINE
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Student model load failed: {exc}") from exc


@app.post("/api/student/chat")
async def student_chat(req: StudentChatRequest, request: Request) -> dict[str, Any]:
    """Run inference on the fine-tuned student model (Qwen3-4B + LoRA).

    Supports two modes:
    - SageMaker Endpoint (STUDENT_ENDPOINT_NAME set)
    - Local model (STUDENT_MODEL_PATH set)
    """
    _check_token(request)
    masked = phi_mask(req.message)

    loop = asyncio.get_running_loop()

    def _infer():
        pipe = _load_student()

        system_prompt = (
            "You are a clinical AI assistant. Answer concisely and cite sources with [N] tags. "
            "If you don't know, say so. End with a Recommendation: line."
        )

        if isinstance(pipe, tuple) and pipe[0] == "sagemaker":
            # SageMaker Endpoint mode
            import json as _json
            import boto3 as _boto3
            endpoint_name = pipe[1]
            # On EC2: use instance profile (no profile_name)
            # Locally: use gapv50k profile
            try:
                session = _boto3.Session(region_name="ap-southeast-1")
                sm_rt = session.client("sagemaker-runtime")
                # Quick check if credentials work
                sm_rt.meta.region_name
            except Exception:
                session = _boto3.Session(
                    profile_name="gapv50k",
                    region_name="ap-southeast-1",
                )
                sm_rt = session.client("sagemaker-runtime")

            system_prompt = (
                "You are a clinical AI assistant. Answer concisely and cite sources with [N] tags. "
                "If you don't know, say so. End with a Recommendation: line."
            )

            if req.emergency:
                # Emergency: force empty think block to skip reasoning, shorter output
                prompt = (
                    f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
                    f"<|im_start|>user\n{masked}<|im_end|>\n"
                    "<|im_start|>assistant\n<think>\n\n</think>\n\n"
                )
                max_new_tokens = 150
            else:
                # Complex: allow thinking for better accuracy
                prompt = (
                    f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
                    f"<|im_start|>user\n{masked}<|im_end|>\n"
                    "<|im_start|>assistant\n"
                )
                max_new_tokens = req.max_new_tokens

            payload = _json.dumps({
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_new_tokens,
                    "temperature": 0.1 if req.emergency else req.temperature,
                    "do_sample": False if req.emergency else req.temperature > 0,
                    "repetition_penalty": 1.1,
                },
            })
            resp = sm_rt.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType="application/json",
                Body=payload,
            )
            result = _json.loads(resp["Body"].read())
            generated = result[0]["generated_text"] if result else ""
            # Extract only the assistant response
            if "<|im_start|>assistant\n" in generated:
                generated = generated.split("<|im_start|>assistant\n")[-1]
            # Strip thinking blocks (empty or full)
            import re as _re
            generated = _re.sub(r"<think>[\s\S]*?</think>\s*", "", generated).strip()
            generated = generated.replace("<|im_end|>", "").strip()
            return generated
        else:
            # Local pipeline mode
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": masked},
            ]
            result = pipe(
                messages,
                max_new_tokens=req.max_new_tokens,
                temperature=req.temperature,
                do_sample=req.temperature > 0,
                return_full_text=False,
            )
            return result[0]["generated_text"] if result else ""

    answer = await loop.run_in_executor(None, _infer)
    return {
        "model": "student",
        "masked_question": masked,
        "answer": answer,
    }


@app.get("/api/student/status")
def student_status() -> dict[str, Any]:
    """Check if the student model is loaded and ready."""
    model_path = os.environ.get("STUDENT_MODEL_PATH", "")
    endpoint_name = os.environ.get("STUDENT_ENDPOINT_NAME", "")
    return {
        "loaded": _STUDENT_PIPELINE is not None,
        "path": model_path or "not configured",
        "endpoint": endpoint_name or "not configured",
        "ready": bool(endpoint_name or model_path),
    }


@app.post("/api/student/stream")
async def student_stream(req: StudentChatRequest, request: Request):
    """SSE streaming endpoint for the student model.

    Calls SageMaker (blocking), then streams the response word-by-word
    so the UI shows progressive output instead of a long blank wait.

    Events:
      event: token   data: {"text": "..."}
      event: done    data: {"elapsed": 3.4}
      event: error   data: {"error": "..."}
    """
    import json as _json
    import time as _time

    _check_token(request)
    masked = phi_mask(req.message)

    loop = asyncio.get_running_loop()

    async def event_generator():
        t0 = _time.time()

        # Run the blocking SageMaker call in a thread
        def _call_sm():
            pipe = _load_student()
            if not (isinstance(pipe, tuple) and pipe[0] == "sagemaker"):
                raise ValueError("Student endpoint not configured")

            import boto3 as _boto3
            endpoint_name = pipe[1]
            try:
                session = _boto3.Session(region_name="ap-southeast-1")
                sm_rt = session.client("sagemaker-runtime")
            except Exception:
                session = _boto3.Session(profile_name="gapv50k", region_name="ap-southeast-1")
                sm_rt = session.client("sagemaker-runtime")

            system_prompt = (
                "You are a clinical AI assistant. Answer concisely and cite sources with [N] tags. "
                "If you don't know, say so. End with a Recommendation: line."
            )

            if req.emergency:
                # Force empty think block to skip reasoning — 2-3x faster
                prompt = (
                    f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
                    f"<|im_start|>user\n{masked}<|im_end|>\n"
                    "<|im_start|>assistant\n<think>\n\n</think>\n\n"
                )
                max_new_tokens = 150
                temperature = 0.1
            else:
                prompt = (
                    f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
                    f"<|im_start|>user\n{masked}<|im_end|>\n"
                    "<|im_start|>assistant\n"
                )
                max_new_tokens = req.max_new_tokens
                temperature = req.temperature

            payload = _json.dumps({
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "do_sample": temperature > 0,
                    "repetition_penalty": 1.1,
                },
            })
            resp = sm_rt.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType="application/json",
                Body=payload,
            )
            result = _json.loads(resp["Body"].read())
            generated = result[0]["generated_text"] if result else ""

            # Extract assistant response
            if "<|im_start|>assistant\n" in generated:
                generated = generated.split("<|im_start|>assistant\n")[-1]
            # Strip thinking blocks
            import re as _re
            generated = _re.sub(r"<think>[\s\S]*?</think>\s*", "", generated).strip()
            generated = generated.replace("<|im_end|>", "").strip()
            return generated

        try:
            answer = await loop.run_in_executor(None, _call_sm)
        except Exception as exc:
            yield f"event: error\ndata: {_json.dumps({'error': str(exc)})}\n\n"
            return

        # Stream word-by-word with a small delay to simulate token streaming
        # Split on spaces but preserve punctuation groupings
        import re as _re
        # Split into ~word-sized chunks preserving markdown
        chunks = _re.split(r'(\s+)', answer)
        buffer = ""
        for chunk in chunks:
            buffer += chunk
            # Emit every 1-3 words or on sentence boundaries
            if len(buffer) >= 8 or any(c in buffer for c in '.!?\n'):
                yield f"event: token\ndata: {_json.dumps({'text': buffer})}\n\n"
                buffer = ""
                await asyncio.sleep(0.02)  # 20ms between chunks = ~50 chunks/sec
        if buffer:
            yield f"event: token\ndata: {_json.dumps({'text': buffer})}\n\n"

        elapsed = _time.time() - t0
        yield f"event: done\ndata: {_json.dumps({'elapsed': round(elapsed, 2)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Root redirect ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(
        '<!doctype html><meta http-equiv="refresh" content="0; url=/ui/index.html">'
    )
