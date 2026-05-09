"""
Nova Health Tech — AI Assistant Lambda.

Minimal demo. Production must:
  - authenticate via Cognito / hospital SSO
  - mask PHI via Comprehend Medical before the Bedrock call
  - enforce Bedrock Guardrails
  - retrieve grounded context from a Bedrock Knowledge Base
  - log to CloudTrail + Bedrock invocation logs (auditable, HIPAA 7-yr)
"""
import json
import os
import boto3

MODEL_ID = os.environ.get("MODEL_ID", "anthropic.claude-haiku-4-5-20251001-v1:0")
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")

bedrock = boto3.client("bedrock-runtime")

SYSTEM_PROMPT = (
    "You are Nova Health Tech's clinical decision-support assistant for internal clinical staff "
    "and hospital clinicians.\n"
    "Rules:\n"
    "  1. Write concise, structured answers in a consistent professional tone.\n"
    "  2. For acute emergency scenarios, lead with the immediate action in one sentence.\n"
    "  3. If you are uncertain or the data is missing, say so and suggest what the clinician should check.\n"
    "  4. Never provide definitive medical advice to patients directly; frame answers for clinicians.\n"
    "  5. Always remind the clinician that your output is decision support, not a diagnosis, "
    "when stakes are high.\n"
    "  6. Do not echo patient identifiers back; if the user shares PHI, redact it in your response.\n"
    "This demo does not yet include Knowledge Base retrieval; cite general clinical knowledge and "
    "flag when information may be out of date."
)


def _response(status, body, stream=False):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
    }
    return {"statusCode": status, "headers": headers, "body": body if stream else json.dumps(body)}


def handler(event, context):
    method = event.get("httpMethod", "POST")
    if method == "OPTIONS":
        return _response(200, {"ok": True})

    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "invalid JSON"})

    user_message = (payload.get("message") or "").strip()
    history = payload.get("history") or []

    if not user_message:
        return _response(400, {"error": "message is required"})

    # Build Converse messages
    messages = []
    for turn in history[-10:]:  # last 10 turns of context
        role = "user" if turn.get("role") == "user" else "assistant"
        content = (turn.get("content") or "").strip()
        if content:
            messages.append({"role": role, "content": [{"text": content}]})
    messages.append({"role": "user", "content": [{"text": user_message}]})

    try:
        resp = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=messages,
            inferenceConfig={"maxTokens": 800, "temperature": 0.2, "topP": 0.9},
        )
    except Exception as exc:  # surface the error to the caller in the demo
        return _response(500, {"error": f"Bedrock call failed: {exc}"})

    # Extract text from Converse response
    output = resp.get("output", {}).get("message", {}).get("content", [])
    text_parts = [block.get("text", "") for block in output if "text" in block]
    answer = "\n".join(p for p in text_parts if p).strip() or "(no response)"

    usage = resp.get("usage", {})

    return _response(
        200,
        {
            "answer": answer,
            "model": MODEL_ID,
            "usage": usage,
            "warning": "Demo response. Production adds Knowledge Base, Guardrails, PHI masking.",
        },
    )
