"""Debug: simulate the exact streaming endpoint flow on EC2 and measure timing."""
import json
import time
import sys
import asyncio
sys.path.insert(0, '/home/ec2-user')

import boto3
from app.graph import (
    _node_phi_mask, _node_pick_lane, _node_cache_lookup,
    _branch_on_lane, _node_emergency_agent, _node_retrieve, ChatState, BEDROCK_REGION
)
from app.agents import DEPARTMENTS, CLAUDE_HAIKU

def run_full_stream_simulation():
    """Simulate exactly what the /api/chat/stream endpoint does."""
    
    # Phase 1: pre-generate (same as server.py _run_pre_generate)
    t0 = time.time()
    state = ChatState(
        question='Patient SpO2 85% on room air with severe COVID-19. What treatment does WHO recommend immediately?',
        emergency=True
    )
    state = _node_phi_mask(state)
    state = _node_pick_lane(state)
    state = _node_cache_lookup(state)
    branch = _branch_on_lane(state)
    if branch == "emergency":
        state = _node_emergency_agent(state)
    state = _node_retrieve(state)
    pre_gen_ms = (time.time() - t0) * 1000
    print(f"Pre-gen: {pre_gen_ms:.0f}ms")

    # Phase 2: build converse payload (same as event_generator in server.py)
    t1 = time.time()
    dept = state.department
    context_parts = []
    for c in state.citations:
        origin = c.get("origin", "vector")
        page = f", page: {c.get('page', 'n/a')}" if c.get("page") else ""
        context_parts.append(
            f"[{c['id']}] (source: {c['source']}{page}, origin: {origin})\n{c['snippet']}"
        )
    context_block = "\n\n".join(context_parts) or "(no context retrieved)"
    user_message = f"Clinical context:\n{context_block}\n\nQuestion:\n{state.masked_question}"
    
    model_id = CLAUDE_HAIKU
    max_tokens = 300
    temperature = 0.1

    converse_kwargs = dict(
        modelId=model_id,
        system=[{"text": dept.system_prompt}],
        messages=[{"role": "user", "content": [{"text": user_message}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
    )
    
    payload_build_ms = (time.time() - t1) * 1000
    print(f"Payload build: {payload_build_ms:.0f}ms")

    # Phase 3: call converse_stream
    t2 = time.time()
    bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
    client_create_ms = (time.time() - t2) * 1000
    print(f"Boto3 client create: {client_create_ms:.0f}ms")
    
    t3 = time.time()
    resp = bedrock.converse_stream(**converse_kwargs)
    api_call_ms = (time.time() - t3) * 1000
    print(f"converse_stream API call: {api_call_ms:.0f}ms")
    
    # Phase 4: iterate stream
    t4 = time.time()
    first_token_time = None
    token_count = 0
    for event in resp.get("stream", []):
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"].get("delta", {})
            text = delta.get("text", "")
            if text:
                token_count += 1
                if first_token_time is None:
                    first_token_time = time.time()
                    stream_ttft_ms = (first_token_time - t3) * 1000
                    print(f"Stream first token (from API call): {stream_ttft_ms:.0f}ms")
        elif "metadata" in event:
            usage = event["metadata"].get("usage", {})
            stream_total_ms = (time.time() - t3) * 1000
            print(f"Stream total: {stream_total_ms:.0f}ms")
            print(f"Tokens: {usage.get('inputTokens', 0)} in / {usage.get('outputTokens', 0)} out")
    
    total_ms = (time.time() - t0) * 1000
    total_ttft_ms = pre_gen_ms + stream_ttft_ms if first_token_time else 0
    print()
    print(f"=== TOTAL TTFT (pre-gen + stream first token): {total_ttft_ms:.0f}ms ===")
    print(f"=== TOTAL end-to-end: {total_ms:.0f}ms ===")
    print(f"=== Boto3 client overhead: {client_create_ms:.0f}ms ===")

run_full_stream_simulation()
print()
print("Running again (boto3 client already warm)...")
print()
run_full_stream_simulation()
