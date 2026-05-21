"""Debug: print the full input payload sent to Bedrock converse_stream for emergency."""
import json
import sys
sys.path.insert(0, '/home/ec2-user')

from app.graph import (
    _node_phi_mask, _node_pick_lane, _node_cache_lookup,
    _node_emergency_agent, _node_retrieve, ChatState
)
from app.agents import DEPARTMENTS, CLAUDE_HAIKU

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

payload = {
    'modelId': CLAUDE_HAIKU,
    'system': [{'text': dept.system_prompt}],
    'messages': [{'role': 'user', 'content': [{'text': user_message}]}],
    'inferenceConfig': {'maxTokens': 300, 'temperature': 0.1},
}
print(json.dumps(payload, indent=2, ensure_ascii=False))
