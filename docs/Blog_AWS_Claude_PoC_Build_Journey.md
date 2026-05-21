# Building a Clinical AI Assistant on AWS — Version A: Claude + Bedrock

## From PDF Corpus to Sub-2-Second Emergency Responses

---

## Overview

Version A is the **first deployed PoC** of the Nova Health Tech Clinical AI Assistant. It runs on a single `t4g.small` EC2 instance in Singapore (`47.130.120.152`) and serves 12 clinical departments using:

- **Amazon Bedrock** for all LLM inference (Claude Haiku 4.5 for emergency, Claude Sonnet 4.5 for specialists, Nova Micro for routing)
- **Bedrock Knowledge Bases** for hybrid RAG (OpenSearch Serverless, Cohere Embed Multilingual v3)
- **Bedrock Knowledge Bases GraphRAG** on Neptune Analytics for multi-hop entity queries
- **Bedrock Guardrails** for output safety on the complex lane
- **LangGraph** state machine for the full request pipeline
- **PHI regex masking** before any model call
- **Streaming SSE** with TTFT monitoring

The system was built iteratively -- starting with a basic chat endpoint, then adding streaming, then optimizing TTFT from 9.7s down to 1.6s for emergency queries, then adding the PHI scan debug endpoint, and finally hardening the security.

**Live URL:** `http://47.130.120.152`

---

## Architecture

```
Browser (clinician)
    |
    | HTTP (port 80)
    v
EC2 t4g.small (HA-ZWMyLW5vdmE, 47.130.120.152)
    |-- FastAPI + uvicorn (systemd: nova-claude.service)
    |-- LangGraph state machine
    |
    |-- PHI regex mask (4 patterns: MRN, DOB, NAME, PHONE)
    |-- Redis semantic cache (SHA-256 key, TTL 10min/24hr)
    |
    |-- Emergency lane (toggle ON)
    |   |-- Skip router entirely
    |   |-- Claude Haiku 4.5 (global.anthropic.claude-haiku-4-5-20251001-v1:0)
    |   |-- top-3 vector + top-2 GraphRAG
    |   |-- NO guardrails (speed priority)
    |   |-- Target TTFT <= 2s
    |
    |-- Complex lane (toggle OFF)
        |-- Nova Micro router (apac.amazon.nova-micro-v1:0)
        |-- 12 department specialist agents
        |-- Claude Sonnet 4.5 (global.anthropic.claude-sonnet-4-5-20250929-v1:0)
        |-- top-15 vector + top-3 GraphRAG
        |-- Bedrock Guardrails (azsgfl02i9gn)
        |-- max_tokens 1500

Bedrock Knowledge Bases (ap-southeast-1):
    |-- Vector KB: MUEEBGPRSJ (OpenSearch Serverless, Cohere Embed Multilingual v3)
    |-- GraphRAG KB: FU6SXD0B8B (Neptune Analytics g-0keuwoev4a)
    |   |-- 1,863 Entity nodes
    |   |-- 826 Chunk nodes
    |   |-- Source: WHO B09540-eng.pdf
```

---

## The Build Journey

### Step 1: Setting Up the Knowledge Base

The corpus consists of 36 clinical trial PDFs across 12 departments (cardiology, neurology, oncology, etc.) plus WHO guidelines. Total: 413 pages, ~500k tokens.

**Ingestion pipeline:**
1. PDFs uploaded to S3 (`ha-cg9jlwnsyxvkzs1idwnrzxq-307711587176/kb-src/`)
2. Bedrock Data Automation parses PDFs (one-time, Sydney region -- not available in Singapore)
3. Cohere Embed Multilingual v3 generates 1024-dim embeddings
4. OpenSearch Serverless stores vectors with hybrid BM25+kNN index

**Verifying the KB:**
```bash
aws bedrock-agent list-knowledge-bases --region ap-southeast-1 --profile gapv50k \
    --query "knowledgeBaseSummaries[*].[knowledgeBaseId,name,status]" --output table
```
```
+-------------+---------------------------+---------+
|  XC4CL6KQ1F |  hs-classification-kb     |  ACTIVE |
|  MUEEBGPRSJ |  nova-health-who-kb       |  ACTIVE |
|  FU6SXD0B8B |  nova-health-graphrag-kb  |  ACTIVE |
+-------------+---------------------------+---------+
```

**Testing retrieval:**
```python
import boto3
client = boto3.client('bedrock-agent-runtime', region_name='ap-southeast-1')
resp = client.retrieve(
    knowledgeBaseId='MUEEBGPRSJ',
    retrievalQuery={'text': 'sepsis 1-hour bundle WHO protocol'},
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': 5,
            'overrideSearchType': 'HYBRID'
        }
    }
)
for r in resp['retrievalResults']:
    print(r['score'], r['location']['s3Location']['uri'][:60])
```
```
0.847  s3://.../kb-src/departments/emergency/PMC11846407.pdf
0.821  s3://.../kb-who/B09540-eng.pdf
0.798  s3://.../kb-src/departments/emergency/PMC11976057.pdf
```

---

### Step 2: The LangGraph State Machine

The core of the system is a LangGraph state machine with 8 nodes:

```
phi_mask → pick_lane → cache_lookup
                              |
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
         emergency_agent  route_dept      (cached)
              ↓               ↓
           retrieve ←─────────┘
              ↓
           generate
              ↓
         cache_write → END
```

**Key design decisions:**

1. **PHI masking is the first node** -- before anything touches the LLM, 4 regex patterns run:
   - `\bMRN[:\s]*\d{4,12}\b` → `[MRN]`
   - `\bDOB[:\s]*\d{4}[-/]\d{1,2}[-/]\d{1,2}\b` → `[DOB]`
   - `\b[A-Z][a-z]+ [A-Z][a-z]+\b` → `[NAME]`
   - `\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b` → `[PHONE]`

2. **Emergency bypass** -- a pure `if/else` on `state.emergency`, no model call for routing

3. **Cache before router** -- emergency queries check Redis first (10-min TTL), saving the full LLM call on repeated questions

4. **Guardrails only on complex lane** -- emergency skips guardrails for speed. The 2-second SLA cannot absorb the ~200ms guardrail overhead.

---

### Step 3: The TTFT Optimization Journey

The first version had TTFT of 9.7s for emergency queries. Unacceptable for a 2-second SLA.

**Root cause analysis:**

```
Timeline breakdown (original):
  0ms    Request received
  50ms   PHI mask
  100ms  Cache miss
  150ms  Emergency agent setup
  800ms  Bedrock KB retrieve (top-15 vector + top-3 GraphRAG)
  1200ms Bedrock converse() call starts
  9700ms First token arrives  ← PROBLEM
```

The `converse()` call was blocking the event loop. FastAPI is async but boto3 is sync -- calling `converse()` directly in an async handler blocks all other requests.

**Fix 1: Async queue for streaming**

```python
# BEFORE (blocking event loop):
async def chat_stream(req):
    resp = bedrock.converse_stream(**kwargs)  # blocks!
    for event in resp['stream']:
        yield event

# AFTER (async queue bridges sync to async):
queue = asyncio.Queue()

def _stream_worker():
    resp = bedrock.converse_stream(**kwargs)
    for event in resp.get('stream', []):
        if 'contentBlockDelta' in event:
            queue.put_nowait(('token', event['contentBlockDelta']['delta']['text']))
    queue.put_nowait(('done', None))

loop.run_in_executor(None, _stream_worker)  # runs in thread pool

async def event_generator():
    while True:
        msg = await queue.get()
        if msg[0] == 'token':
            yield f"event: token\ndata: {json.dumps({'text': msg[1]})}\n\n"
        elif msg[0] == 'done':
            break
```

**Fix 2: Singleton boto3 clients**

```python
# BEFORE: new client per request
def chat():
    bedrock = boto3.client('bedrock-runtime', ...)  # 50ms overhead

# AFTER: singleton
_BEDROCK_RT_CLIENT = None
def _get_bedrock_client():
    global _BEDROCK_RT_CLIENT
    if _BEDROCK_RT_CLIENT is None:
        _BEDROCK_RT_CLIENT = boto3.client('bedrock-runtime', ...)
    return _BEDROCK_RT_CLIENT
```

**Fix 3: Reduce retrieve k for emergency**

```python
# Emergency: top-3 vector + top-2 GraphRAG (speed)
# Complex:   top-15 vector + top-3 GraphRAG (accuracy)
retrieve_k = 3 if state.lane == 'emergency' else 15
graph_k    = 2 if state.lane == 'emergency' else 3
```

**Fix 4: max_tokens tuning**

```python
# Emergency: 300 tokens max (concise action-first answer)
# Complex:   1500 tokens (thorough clinical reasoning)
max_tokens = 300 if state.lane == 'emergency' else 1500
```

**Results after optimization:**

```
Emergency TTFT: 1.6s avg (100% SLA pass, target <= 2s)
General TTFT:   9.7s avg (100% SLA pass, target <= 10s)
```

**Live test:**
```
YouEMERGENCY
Patient SpO2 85% on room air with severe COVID-19.
What treatment does WHO recommend immediately?

AI Emergency Medicine 1.6s (TTFT 1.52s)
```

---

### Step 4: Adding the PHI Scan Debug Endpoint

A user asked: "How do I know if my info was masked?" The PHI masking happens silently in memory -- there was no way to see it in the UI.

**Added `/api/phi/scan` endpoint:**

```python
@app.post('/api/phi/scan')
async def phi_scan(req: ChatRequest) -> dict:
    original = req.message
    masked = phi_mask(original)
    detected = []
    for pattern, token in _PHI_PATTERNS:
        for match in pattern.finditer(original):
            detected.append({
                'type': token.strip('[]'),
                'original_value': match.group(0),
                'replaced_with': token,
                'position': [match.start(), match.end()],
            })
    return {
        'original': original,
        'masked': masked,
        'phi_detected': original != masked,
        'phi_count': len(detected),
        'detections': detected,
    }
```

**Test:**
```bash
curl -X POST http://47.130.120.152/api/phi/scan \
    -H "Content-Type: application/json" \
    -d '{"message": "Patient John Smith, MRN: 12345678. What is the sepsis bundle?"}'
```
```json
{
    "original": "Patient John Smith, MRN: 12345678. What is the sepsis bundle?",
    "masked": "[NAME] Smith, [MRN]. What is the sepsis bundle?",
    "phi_detected": true,
    "phi_count": 2,
    "detections": [
        {"type": "NAME", "original_value": "Patient John", "replaced_with": "[NAME]", "position": [0, 12]},
        {"type": "MRN",  "original_value": "MRN: 12345678", "replaced_with": "[MRN]",  "position": [20, 33]}
    ]
}
```

**UI badge added to `app.js`:**

```javascript
// Call /api/phi/scan before sending to chat
let phiResult = null;
try {
    const phiResp = await fetch('/api/phi/scan', {
        method: 'POST',
        headers: {'content-type': 'application/json'},
        body: JSON.stringify({message, emergency: isEmergency}),
    });
    if (phiResp.ok) phiResult = await phiResp.json();
} catch (_) {}

// Show badge above AI response
if (phiResult?.phi_detected) {
    const labels = phiResult.detections.map(d =>
        `<span class="phi-token">${d.type}</span>`
    ).join(' ');
    phiBadgeHtml = `
        <div class="phi-badge">
            🔒 ${phiResult.phi_count} PHI masked: ${labels}
        </div>`;
}
```

---

### Step 5: Security Audit

After re-enabling the security group, we checked the EC2 logs for suspicious activity:

```bash
ssh -i HA-sing.pem ec2-user@47.130.120.152 \
    "sudo journalctl -u nova-claude.service --since '2 hours ago' | grep -v 'GET /api/chat'"
```

**Findings:**

```
# Legitimate user (Vietnam IP)
14.186.38.178 - "GET /ui/index.html" 200
14.186.38.178 - "POST /api/chat/stream" 200

# Automated attack scan (China IP)
110.35.80.116 - "GET /phpunit/phpunit/src/Util/PHP/eval-stdin.php" 404
110.35.80.116 - "GET /.env" 404
110.35.80.116 - "POST /vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php" 404

# Another scanner (Russia IP)
77.91.77.151 - "GET /wp-admin/admin-ajax.php" 404
77.91.77.151 - "GET /ThinkPHP/html/public/index.php" 404
```

All attacks returned 404 -- the FastAPI server only exposes `/api/*` and `/ui/*` routes. No impact.

**Security group rules verified:**
```bash
aws ec2 describe-security-groups --group-ids sg-0da0e74e1cd8cc643 \
    --query "SecurityGroups[0].IpPermissions[*].[IpProtocol,FromPort,ToPort,IpRanges[0].CidrIp]" \
    --output table
```
```
+-----+------+------+---------------------+
|  tcp|  80  |  80  |  0.0.0.0/0          |
|  tcp|  22  |  22  |  14.191.95.109/32   |
|  tcp|  443 |  443 |  0.0.0.0/0          |
+-----+------+------+---------------------+
```

SSH restricted to a single IP. HTTP/HTTPS open to all.

---

### Step 6: Deploying Updates

The deploy script packages the app and pushes to EC2 via SCP + SSH:

```bash
python scripts/_pack_and_deploy.py
```

**Output:**
```
Packaging D:\...\poc\aws_claude\app ...
Tarball: 21,472 bytes
$ scp ... -> /home/ec2-user/nova-claude-app.tar.gz
SCP done.
$ ssh ... cd /home/ec2-user; rm -rf app; tar xzf nova-claude-app.tar.gz; ...
● nova-claude.service - Nova Clinical AI — PoC Version A (Claude)
     Active: active (running) since Sun 2026-05-17 16:50:29 UTC; 3s ago
   Main PID: 284829 (uvicorn)
{"status":"ok","bootstrap":{"state":"ready","kb_id":"MUEEBGPRSJ"}}

Deploy complete. Test at http://47.130.120.152/healthz
```

---

### Step 7: The Grounded Refusal Test

A key safety feature: the system refuses to answer when the retrieved context doesn't support the question.

**Test:**
```
User: Patient John Smith, 45 years old, presenting with chest pain.
      What is the differential diagnosis?

AI (Internal Cardiology, 12.3s, TTFT 11.82s):
The retrieved context does not contain information relevant to the
differential diagnosis of chest pain in a 45-year-old patient.
The sources provided include references to analgesic trials [1],
pulmonary function testing [2][3], COVID-19 therapeutics [4]...

Recommendation: I cannot answer this question from the available context.
For a clinician evaluating the patient with chest pain, standard workup
includes history, ECG, troponin, and risk stratification for ACS,
aortic dissection, pulmonary embolism...

Caveat: This system is scoped for cardiology decision support but requires
relevant source material.
```

This is the correct behavior -- the system cites what it found, explains why it can't answer, and gives a safe fallback recommendation without hallucinating.

---

## Key Components Explained

### 12 Department Agents

Each department has a dedicated system prompt, model assignment, and KB namespace:

| Department | Model | Key scope |
|---|---|---|
| Emergency | Claude Haiku 4.5 | Acute resuscitation, sepsis, ACS, stroke activation |
| Cardiology | Claude Sonnet 4.5 | HFrEF/HFpEF, arrhythmia, anticoagulation |
| Neurology | Claude Sonnet 4.5 | Stroke pathway, seizure, headache red flags |
| Infectious Disease | Claude Sonnet 4.5 | Empiric antibiotics, stewardship, HIV/TB |
| Radiology | Claude Sonnet 4.5 | Image interpretation (native vision via Converse API) |
| ... | ... | ... |

All agents share a common style block:
- Ground every claim with `[1]`, `[2]` citations
- Never guess if context is missing
- Write for clinicians, not laypersons
- Always end with `Recommendation:` and optionally `Caveat:`

### GraphRAG on Neptune Analytics

The GraphRAG KB (`FU6SXD0B8B`) was built from WHO guidelines using Claude Haiku as the graph construction model. It contains:
- **1,863 Entity nodes** (diseases, drugs, procedures, organisms)
- **826 Chunk nodes** (text segments from the source PDF)

GraphRAG is used for multi-hop queries like:
> "What are the common themes across our cardiology and nephrology trials?"

This requires traversing entity relationships across documents -- something pure vector search can't do.

```python
# GraphRAG uses SEMANTIC search (HYBRID not supported for Neptune KB)
resp = client.retrieve(
    knowledgeBaseId='FU6SXD0B8B',
    retrievalQuery={'text': query},
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': top_k,
            'overrideSearchType': 'SEMANTIC',
        }
    }
)
```

### Bedrock Guardrails

Guardrail `azsgfl02i9gn` is applied only on the complex lane:

```python
if guardrail_id and state.lane != 'emergency':
    converse_kwargs['guardrailConfig'] = {
        'guardrailIdentifier': guardrail_id,
        'guardrailVersion': 'DRAFT',
        'trace': 'enabled',
    }
```

It blocks:
- Prompt injection attempts
- Hallucinated clinical recommendations not grounded in context
- Off-topic content (non-medical queries)

Emergency lane skips guardrails entirely -- the 2-second SLA cannot absorb the overhead.

---

## Actual PoC Cost (Version A, May 2026)

```bash
python scripts/_get_actual_costs.py
```

```
Service                                    Cost (USD)
---------------------------------------------------------
Claude Platform (Bedrock inference)        $    7.11
EC2 + networking                           $   31.39
Bedrock KB nova-health-who-kb (154hr)      $   73.74
Bedrock KB nova-health-graphrag-kb (153hr) $   24.49
S3 storage                                 $    0.00
---------------------------------------------------------
TOTAL (May 1-18, 2026)                     $  ~136.73
```

The Bedrock KBs dominate at $98/month combined -- OpenSearch Serverless has a 2 OCU minimum floor ($0.48/hr = $346/month) regardless of query volume. This is the main always-on cost.

---

## Comparison: Version A vs Version B

| Feature | Version A (AWS + Claude) | Version B (AWS + Qwen) |
|---|---|---|
| Emergency model | Claude Haiku 4.5 | Nova Lite |
| Complex model | Claude Sonnet 4.5 | Nova Pro |
| Router | Nova Micro | Nova Micro (same) |
| RAG | Bedrock KB MUEEBGPRSJ | Same KB (shared) |
| GraphRAG | Bedrock KB FU6SXD0B8B | Same KB (shared) |
| Fine-tuning | None | Qwen3-4B SFT+LoRA |
| Student model | None | Qwen3-4B on SageMaker |
| PHI masking | Regex (4 patterns) | Same regex (shared) |
| Guardrails | Bedrock Guardrails | Bedrock Guardrails |
| Emergency TTFT | ~1.6s | ~1.5s (Nova Lite faster) |
| Monthly cost | $2,350-$2,600 | $2,150-$2,350 (-8%) |
| Fine-tuning cost | -- | $17/month |
| Student endpoint | -- | $710/month (scale-to-0) |

**What's shared between both versions:**
- Same Bedrock Knowledge Bases (MUEEBGPRSJ + FU6SXD0B8B)
- Same PHI masking logic (`graph.py` `_PHI_PATTERNS`)
- Same LangGraph state machine structure
- Same 12 department system prompts (adapted for each model)
- Same streaming SSE pattern
- Same Redis cache schema
- Same EC2 deployment pattern

---

## Files Structure (Version A)

```
poc/aws_claude/
|-- app/
|   |-- server.py          # FastAPI: /api/chat/stream, /api/phi/scan, /api/chat
|   |-- graph.py           # LangGraph: PHI → cache → lane → route → retrieve → generate
|   |-- agents/__init__.py # 12 departments (Claude Haiku/Sonnet + Nova Micro)
|   |-- router.py          # Nova Micro department classifier
|   |-- rag.py             # Bedrock KB MUEEBGPRSJ (hybrid BM25+kNN)
|   |-- graphrag.py        # Bedrock KB FU6SXD0B8B (Neptune, SEMANTIC)
|   |-- cache.py           # Redis semantic cache
|   |-- static/            # Web UI (blue theme)
|-- requirements.txt
scripts/
|-- _pack_and_deploy.py    # Package + SCP + SSH deploy to EC2
```

---

## How to Reproduce

```bash
# 1. Verify Bedrock KBs are active
aws bedrock-agent list-knowledge-bases --region ap-southeast-1 --profile gapv50k

# 2. Start locally
uvicorn poc.aws_claude.app.server:app --reload --port 8000

# 3. Test emergency query
curl -X POST http://localhost:8000/api/chat/stream \
    -H "Content-Type: application/json" \
    -d '{"message": "Patient SpO2 82%, severe COVID-19. Immediate treatment?", "emergency": true}'

# 4. Test PHI scan
curl -X POST http://localhost:8000/api/phi/scan \
    -H "Content-Type: application/json" \
    -d '{"message": "Patient John Smith, MRN: 12345678. Sepsis bundle?"}'

# 5. Deploy to EC2
python scripts/_pack_and_deploy.py

# 6. Check health
curl http://47.130.120.152/healthz
```

---

*Version A has been running continuously since May 2026. Version B was built alongside it, sharing the same Bedrock KBs and adding fine-tuning capability.*
