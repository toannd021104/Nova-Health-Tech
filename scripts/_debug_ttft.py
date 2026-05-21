"""Debug: measure actual TTFT from converse_stream on EC2 with different configs."""
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

# Build the same state
state = ChatState(
    question='Patient SpO2 85% on room air with severe COVID-19. What treatment does WHO recommend immediately?',
    emergency=True
)
state = _node_phi_mask(state)
state = _node_pick_lane(state)
state = _node_cache_lookup(state)
state = _node_emergency_agent(state)
state = _node_retrieve(state)

dept = state.department
context_parts = []
for c in state.citations:
    origin = c.get('origin', 'vector')
    page = f", page: {c.get('page', 'n/a')}" if c.get('page') else ''
    context_parts.append(
        f"[{c['id']}] (source: {c['source']}{page}, origin: {origin})\n{c['snippet']}"
    )
context_block = '\n\n'.join(context_parts) or '(no context retrieved)'
user_message = f'Clinical context:\n{context_block}\n\nQuestion:\n{state.masked_question}'

bedrock = boto3.client("bedrock-runtime", region_name="ap-southeast-1")

# Test 1: Current config (temp=0.1, maxTokens=300)
print("=" * 60)
print("TEST 1: temp=0.1, maxTokens=300 (current emergency config)")
print("=" * 60)
t0 = time.time()
resp = bedrock.converse_stream(
    modelId=CLAUDE_HAIKU,
    system=[{"text": dept.system_prompt}],
    messages=[{"role": "user", "content": [{"text": user_message}]}],
    inferenceConfig={"maxTokens": 300, "temperature": 0.1},
)
first_token_text = None
for event in resp.get("stream", []):
    if "contentBlockDelta" in event:
        delta = event["contentBlockDelta"].get("delta", {})
        text = delta.get("text", "")
        if text and first_token_text is None:
            first_token_text = text
            ttft = time.time() - t0
            print(f"  TTFT: {ttft*1000:.0f}ms")
            print(f"  First token: {repr(text)}")
    elif "metadata" in event:
        usage = event["metadata"].get("usage", {})
        total = time.time() - t0
        print(f"  Total: {total*1000:.0f}ms")
        print(f"  Tokens: {usage.get('inputTokens', 0)} in / {usage.get('outputTokens', 0)} out")

print()
time.sleep(2)

# Test 2: temp=1, maxTokens=32000 (like the playground)
print("=" * 60)
print("TEST 2: temp=1, maxTokens=4096 (playground-like)")
print("=" * 60)
t0 = time.time()
resp = bedrock.converse_stream(
    modelId=CLAUDE_HAIKU,
    system=[{"text": dept.system_prompt}],
    messages=[{"role": "user", "content": [{"text": user_message}]}],
    inferenceConfig={"maxTokens": 4096, "temperature": 1.0},
)
first_token_text = None
for event in resp.get("stream", []):
    if "contentBlockDelta" in event:
        delta = event["contentBlockDelta"].get("delta", {})
        text = delta.get("text", "")
        if text and first_token_text is None:
            first_token_text = text
            ttft = time.time() - t0
            print(f"  TTFT: {ttft*1000:.0f}ms")
            print(f"  First token: {repr(text)}")
    elif "metadata" in event:
        usage = event["metadata"].get("usage", {})
        total = time.time() - t0
        print(f"  Total: {total*1000:.0f}ms")
        print(f"  Tokens: {usage.get('inputTokens', 0)} in / {usage.get('outputTokens', 0)} out")

print()
time.sleep(2)

# Test 3: No system prompt, temp=1
print("=" * 60)
print("TEST 3: NO system prompt, temp=1, maxTokens=4096")
print("=" * 60)
t0 = time.time()
resp = bedrock.converse_stream(
    modelId=CLAUDE_HAIKU,
    messages=[{"role": "user", "content": [{"text": user_message}]}],
    inferenceConfig={"maxTokens": 4096, "temperature": 1.0},
)
first_token_text = None
for event in resp.get("stream", []):
    if "contentBlockDelta" in event:
        delta = event["contentBlockDelta"].get("delta", {})
        text = delta.get("text", "")
        if text and first_token_text is None:
            first_token_text = text
            ttft = time.time() - t0
            print(f"  TTFT: {ttft*1000:.0f}ms")
            print(f"  First token: {repr(text)}")
    elif "metadata" in event:
        usage = event["metadata"].get("usage", {})
        total = time.time() - t0
        print(f"  Total: {total*1000:.0f}ms")
        print(f"  Tokens: {usage.get('inputTokens', 0)} in / {usage.get('outputTokens', 0)} out")

print()
time.sleep(2)

# Test 4: Minimal input (just the question, no context)
print("=" * 60)
print("TEST 4: Minimal input (question only, no context, no system)")
print("=" * 60)
t0 = time.time()
resp = bedrock.converse_stream(
    modelId=CLAUDE_HAIKU,
    messages=[{"role": "user", "content": [{"text": "Patient SpO2 85% on room air with severe COVID-19. What treatment does WHO recommend immediately?"}]}],
    inferenceConfig={"maxTokens": 4096, "temperature": 1.0},
)
first_token_text = None
for event in resp.get("stream", []):
    if "contentBlockDelta" in event:
        delta = event["contentBlockDelta"].get("delta", {})
        text = delta.get("text", "")
        if text and first_token_text is None:
            first_token_text = text
            ttft = time.time() - t0
            print(f"  TTFT: {ttft*1000:.0f}ms")
            print(f"  First token: {repr(text)}")
    elif "metadata" in event:
        usage = event["metadata"].get("usage", {})
        total = time.time() - t0
        print(f"  Total: {total*1000:.0f}ms")
        print(f"  Tokens: {usage.get('inputTokens', 0)} in / {usage.get('outputTokens', 0)} out")
