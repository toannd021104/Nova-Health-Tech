"""Debug: measure pre-gen + model TTFT separately on EC2."""
import json
import time
import sys
sys.path.insert(0, '/home/ec2-user')

import boto3
from app.graph import (
    _node_phi_mask, _node_pick_lane, _node_cache_lookup,
    _node_emergency_agent, _node_retrieve, ChatState
)
from app.agents import DEPARTMENTS, CLAUDE_HAIKU

print("=" * 60)
print("PHASE 1: Pre-generate (phi_mask + pick_lane + retrieve)")
print("=" * 60)

t0 = time.time()
state = ChatState(
    question='Patient SpO2 85% on room air with severe COVID-19. What treatment does WHO recommend immediately?',
    emergency=True
)
state = _node_phi_mask(state)
state = _node_pick_lane(state)
state = _node_cache_lookup(state)
state = _node_emergency_agent(state)
t_retrieve_start = time.time()
state = _node_retrieve(state)
t_retrieve_end = time.time()
pre_gen_total = time.time() - t0

print(f"  Retrieve: {(t_retrieve_end - t_retrieve_start)*1000:.0f}ms")
print(f"  Pre-gen total: {pre_gen_total*1000:.0f}ms")
print(f"  Citations: {len(state.citations)}")

# Build the converse payload
dept = state.department
context_parts = []
for c in state.citations:
    origin = c.get('origin', 'vector')
    page = f", page: {c.get('page', 'n/a')}" if c.get('page') else ''
    context_parts.append(
        f"[{c['id']}] (source: {c['source']}{page}, origin: {origin})\n{c['snippet']}"
    )
context_block = '\n\n'.join(context_parts)
user_message = f'Clinical context:\n{context_block}\n\nQuestion:\n{state.masked_question}'

print()
print("=" * 60)
print("PHASE 2: converse_stream (Haiku 4.5)")
print("=" * 60)

bedrock = boto3.client("bedrock-runtime", region_name="ap-southeast-1")

t1 = time.time()
resp = bedrock.converse_stream(
    modelId=CLAUDE_HAIKU,
    system=[{"text": dept.system_prompt}],
    messages=[{"role": "user", "content": [{"text": user_message}]}],
    inferenceConfig={"maxTokens": 300, "temperature": 0.1},
)
first_token_text = None
token_count = 0
for event in resp.get("stream", []):
    if "contentBlockDelta" in event:
        delta = event["contentBlockDelta"].get("delta", {})
        text = delta.get("text", "")
        if text:
            token_count += 1
            if first_token_text is None:
                first_token_text = text
                model_ttft = time.time() - t1
                print(f"  Model TTFT: {model_ttft*1000:.0f}ms")
    elif "metadata" in event:
        usage = event["metadata"].get("usage", {})
        model_total = time.time() - t1
        print(f"  Model total: {model_total*1000:.0f}ms")
        print(f"  Tokens: {usage.get('inputTokens', 0)} in / {usage.get('outputTokens', 0)} out")
        print(f"  Stream events: {token_count}")

end_to_end = time.time() - t0
print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Pre-gen:    {pre_gen_total*1000:.0f}ms")
print(f"  Model TTFT: {model_ttft*1000:.0f}ms")
print(f"  Model gen:  {(model_total - model_ttft)*1000:.0f}ms")
print(f"  End-to-end: {end_to_end*1000:.0f}ms")
print(f"  Expected browser TTFT: {(pre_gen_total + model_ttft)*1000:.0f}ms + network RTT")
