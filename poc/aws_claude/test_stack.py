"""
Detailed test of the Nova Health managed stack.

Tests two cases:
  Case 1 — Emergency: acute clinical question, expects fast grounded answer
  Case 2 — Complex:   multi-step diagnostic question, expects structured answer with citations

Measures:
  - Time to first token (TTFT)
  - Total response time
  - Total tokens (input + output)
  - Number of retrieved KB chunks
  - Guardrail events
  - Retrieval latency (via Bedrock KB Retrieve API separately)
  - Agent invocation trace (citations, reasoning steps)

Usage:
    python poc/aws_claude/test_stack.py
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

import boto3

PROFILE = "gapv50k"
REGION = "ap-southeast-1"

# Load outputs from deploy
OUTPUTS = json.loads((Path(__file__).parent / ".managed_outputs.json").read_text())
KB_ID = OUTPUTS["kb_id"]
GRAPHRAG_KB_ID = OUTPUTS.get("graphrag_kb_id", "")
AGENT_ID = OUTPUTS["agent_id"]
GUARDRAIL_ID = OUTPUTS["guardrail_id"]
GUARDRAIL_VERSION = "DRAFT"

# Models — must use inference profile IDs for RetrieveAndGenerate and Converse
MODEL_EMERGENCY = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
MODEL_COMPLEX = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"

# For Bedrock Agent (uses foundation model ID directly)
AGENT_MODEL_EMERGENCY = "anthropic.claude-haiku-4-5-20251001-v1:0"
AGENT_MODEL_COMPLEX = "anthropic.claude-sonnet-4-5-20250929-v1:0"

# ─────────────────────────────────────────────────────────────────────────────
# Test cases
# ─────────────────────────────────────────────────────────────────────────────

CASES = [
    {
        "id": "CASE-1-EMERGENCY",
        "label": "Emergency: acute STEMI dosing",
        "model": MODEL_EMERGENCY,
        "query": (
            "Patient presents with acute STEMI, ongoing chest pain, BP 110/70, HR 88. "
            "What is the recommended antiplatelet loading dose and timing according to WHO guidelines? "
            "Be concise."
        ),
        "expected_keywords": ["aspirin", "clopidogrel", "ticagrelor", "loading", "mg"],
        "sla_ttft_ms": 2000,
        "sla_total_ms": 5000,
    },
    {
        "id": "CASE-2-COMPLEX",
        "label": "Complex: COVID-19 treatment protocol for hospitalised patient",
        "model": MODEL_COMPLEX,
        "query": (
            "According to WHO guidelines, what is the recommended treatment protocol for a hospitalised "
            "adult patient with severe COVID-19 who requires supplemental oxygen but is not yet on "
            "mechanical ventilation? Include drug names, dosing, and evidence grading where available. "
            "Cite your sources."
        ),
        "expected_keywords": ["dexamethasone", "oxygen", "corticosteroid", "remdesivir", "WHO"],
        "sla_ttft_ms": 4000,
        "sla_total_ms": 15000,
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def hr(char: str = "─", width: int = 72) -> str:
    return char * width


def check_keywords(text: str, keywords: list[str]) -> dict[str, bool]:
    lower = text.lower()
    return {kw: kw.lower() in lower for kw in keywords}


def format_ms(ms: float) -> str:
    if ms < 1000:
        return f"{ms:.0f} ms"
    return f"{ms / 1000:.2f} s"


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Direct KB Retrieve (measures pure retrieval latency)
# ─────────────────────────────────────────────────────────────────────────────

def test_kb_retrieve(bedrock_agent_runtime, query: str, case_id: str, kb_id: str = None, label: str = "Vector KB") -> dict[str, Any]:
    """Call Bedrock KB Retrieve directly to measure retrieval latency."""
    if kb_id is None:
        kb_id = KB_ID
    # GraphRAG KB only supports SEMANTIC; Vector KB supports HYBRID
    is_graphrag = kb_id == GRAPHRAG_KB_ID
    search_type = "SEMANTIC" if is_graphrag else "HYBRID"
    print(f"\n  [{label}] Querying KB {kb_id} (search={search_type})...")
    t0 = time.perf_counter()
    resp = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": 5,
                "overrideSearchType": search_type,
            }
        },
    )
    retrieval_ms = (time.perf_counter() - t0) * 1000
    chunks = resp.get("retrievalResults", [])

    print(f"  [{label}] Done in {format_ms(retrieval_ms)}")
    print(f"  [{label}] Chunks returned: {len(chunks)}")
    for i, chunk in enumerate(chunks, 1):
        score = chunk.get("score", 0)
        loc = chunk.get("location", {})
        s3_loc = loc.get("s3Location", {})
        uri = s3_loc.get("uri", "unknown")
        text_preview = chunk.get("content", {}).get("text", "")[:120].replace("\n", " ")
        print(f"    [{i}] score={score:.4f}  uri={uri}")
        print(f"         preview: {text_preview}...")

    return {
        "retrieval_ms": retrieval_ms,
        "num_chunks": len(chunks),
        "chunks": [
            {
                "score": c.get("score", 0),
                "uri": c.get("location", {}).get("s3Location", {}).get("uri", ""),
                "text_preview": c.get("content", {}).get("text", "")[:200],
            }
            for c in chunks
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Bedrock Agent invoke with streaming (measures TTFT + total)
# ─────────────────────────────────────────────────────────────────────────────

def test_agent_invoke(bedrock_agent_runtime, case: dict) -> dict[str, Any]:
    """Invoke the Bedrock Agent with streaming and measure TTFT."""
    session_id = str(uuid.uuid4())
    query = case["query"]
    model = case["model"]

    print(f"\n  [Agent] Invoking agent {AGENT_ID} with model {model}")
    print(f"  [Agent] Session: {session_id}")

    t_start = time.perf_counter()
    t_first_token = None
    full_text = ""
    trace_events = []
    guardrail_events = []
    input_tokens = 0
    output_tokens = 0

    resp = bedrock_agent_runtime.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId="TSTALIASID",  # DRAFT alias
        sessionId=session_id,
        inputText=query,
        enableTrace=True,
    )

    event_stream = resp["completion"]

    for event in event_stream:
        now = time.perf_counter()

        # Chunk event (actual text tokens)
        if "chunk" in event:
            chunk_bytes = event["chunk"].get("bytes", b"")
            chunk_text = chunk_bytes.decode("utf-8", errors="replace")
            if chunk_text and t_first_token is None:
                t_first_token = now
                ttft_ms = (t_first_token - t_start) * 1000
                print(f"\n  [Agent] FIRST TOKEN at {format_ms(ttft_ms)}")
                print(f"  [Agent] First token preview: {repr(chunk_text[:80])}")
            full_text += chunk_text

            # Attribution / citations
            attribution = event["chunk"].get("attribution", {})
            if attribution:
                citations = attribution.get("citations", [])
                for cit in citations:
                    refs = cit.get("retrievedReferences", [])
                    for ref in refs:
                        uri = ref.get("location", {}).get("s3Location", {}).get("uri", "")
                        trace_events.append({"type": "citation", "uri": uri})

        # Trace event (reasoning steps, retrieval, guardrail)
        elif "trace" in event:
            trace = event["trace"].get("trace", {})

            # Guardrail trace
            if "guardrailTrace" in trace:
                gt = trace["guardrailTrace"]
                action = gt.get("action", "")
                guardrail_events.append({"action": action, "trace": gt})
                print(f"  [Guardrail] action={action}")

            # Orchestration trace (reasoning + retrieval)
            if "orchestrationTrace" in trace:
                ot = trace["orchestrationTrace"]

                # Model invocation input (captures input tokens)
                if "modelInvocationInput" in ot:
                    pass  # token counts come from output

                # Model invocation output (captures token usage)
                if "modelInvocationOutput" in ot:
                    usage = ot["modelInvocationOutput"].get("metadata", {}).get("usage", {})
                    input_tokens += usage.get("inputTokens", 0)
                    output_tokens += usage.get("outputTokens", 0)

                # Rationale (reasoning step)
                if "rationale" in ot:
                    text = ot["rationale"].get("text", "")[:100]
                    print(f"  [Reasoning] {text}...")

                # Invocation input (tool call)
                if "invocationInput" in ot:
                    inv = ot["invocationInput"]
                    if "knowledgeBaseLookupInput" in inv:
                        kb_query = inv["knowledgeBaseLookupInput"].get("text", "")
                        print(f"  [KB Lookup] query: {kb_query[:80]}")

                # Observation (tool result)
                if "observation" in ot:
                    obs = ot["observation"]
                    if "knowledgeBaseLookupOutput" in obs:
                        refs = obs["knowledgeBaseLookupOutput"].get("retrievedReferences", [])
                        print(f"  [KB Result] {len(refs)} chunks retrieved")

        # Return control (shouldn't happen for KB-only agent)
        elif "returnControl" in event:
            print(f"  [ReturnControl] {event['returnControl']}")

    t_end = time.perf_counter()
    total_ms = (t_end - t_start) * 1000
    ttft_ms = (t_first_token - t_start) * 1000 if t_first_token else total_ms

    return {
        "ttft_ms": ttft_ms,
        "total_ms": total_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "full_text": full_text,
        "trace_events": trace_events,
        "guardrail_events": guardrail_events,
        "session_id": session_id,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Direct Converse (no agent, just model + KB retrieve-and-generate)
# ─────────────────────────────────────────────────────────────────────────────

def test_retrieve_and_generate(bedrock_agent_runtime, case: dict) -> dict[str, Any]:
    """Use RetrieveAndGenerate for a simpler end-to-end test with TTFT measurement."""
    query = case["query"]
    model = case["model"]

    print(f"\n  [RAG] RetrieveAndGenerate with model {model}")

    t_start = time.perf_counter()
    resp = bedrock_agent_runtime.retrieve_and_generate(
        input={"text": query},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KB_ID,
                "modelArn": f"arn:aws:bedrock:{REGION}:307711587176:inference-profile/{model}",
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {
                        "numberOfResults": 5,
                        "overrideSearchType": "HYBRID",
                    }
                },
                "generationConfiguration": {
                    "inferenceConfig": {
                        "textInferenceConfig": {
                            "maxTokens": 1024,
                            "temperature": 0.1,
                        }
                    },
                    "promptTemplate": {
                        "textPromptTemplate": (
                            "You are a clinical decision-support assistant. "
                            "Answer the question using ONLY the provided context. "
                            "Cite sources with [1], [2] etc. "
                            "If the context does not contain enough information, say so explicitly.\n\n"
                            "$search_results$\n\n"
                            "Question: $query$\n\n"
                            "Answer:"
                        )
                    },
                },
            },
        },
    )
    total_ms = (time.perf_counter() - t_start) * 1000

    output_text = resp.get("output", {}).get("text", "")
    citations = resp.get("citations", [])
    session_id = resp.get("sessionId", "")

    # Count retrieved chunks across all citations
    all_refs = []
    for cit in citations:
        refs = cit.get("retrievedReferences", [])
        all_refs.extend(refs)

    print(f"  [RAG] Total time: {format_ms(total_ms)}")
    print(f"  [RAG] Citations: {len(citations)}, total refs: {len(all_refs)}")

    return {
        "total_ms": total_ms,
        "output_text": output_text,
        "num_citations": len(citations),
        "num_refs": len(all_refs),
        "session_id": session_id,
        "refs": [
            {
                "uri": r.get("location", {}).get("s3Location", {}).get("uri", ""),
                "text_preview": r.get("content", {}).get("text", "")[:200],
            }
            for r in all_refs[:5]
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Converse streaming with retrieved context (accurate TTFT measurement)
# ─────────────────────────────────────────────────────────────────────────────

def test_converse_streaming(bedrock_runtime, case: dict, retrieved_chunks: list) -> dict[str, Any]:
    """
    Converse API with streaming using retrieved chunks as context.
    This gives the most accurate TTFT measurement since we control the stream.
    """
    model = case["model"]
    query = case["query"]

    # Build context from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        text = chunk.get("text_preview", "")
        uri = chunk.get("uri", "")
        context_parts.append(f"[{i}] Source: {uri}\n{text}")
    context = "\n\n".join(context_parts)

    system_prompt = (
        "You are a clinical decision-support assistant for Nova Health Tech. "
        "Answer the question using ONLY the provided context from WHO guidelines. "
        "Cite sources with [1], [2] etc. "
        "If the context does not contain enough information, say so explicitly. "
        "Never provide a diagnosis. Be concise for emergency queries."
    )

    user_message = f"Context from WHO guidelines:\n\n{context}\n\nQuestion: {query}"

    print(f"\n  [Converse] Model: {model}")
    print(f"  [Converse] Context chunks: {len(retrieved_chunks)}")
    print(f"  [Converse] Prompt length: ~{len(user_message) // 4} tokens (estimated)")

    t_start = time.perf_counter()
    t_first_token = None
    full_text = ""
    input_tokens = 0
    output_tokens = 0

    resp = bedrock_runtime.converse_stream(
        modelId=model,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": user_message}]}],
        inferenceConfig={
            "maxTokens": 1024,
            "temperature": 0.1,
        },
        guardrailConfig={
            "guardrailIdentifier": GUARDRAIL_ID,
            "guardrailVersion": GUARDRAIL_VERSION,
            "trace": "enabled",
        },
    )

    stream = resp.get("stream")
    guardrail_events = []
    for event in stream:
        now = time.perf_counter()

        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"].get("delta", {})
            text = delta.get("text", "")
            if text:
                if t_first_token is None:
                    t_first_token = now
                    ttft_ms = (t_first_token - t_start) * 1000
                    print(f"\n  [Converse] FIRST TOKEN at {format_ms(ttft_ms)}")
                    print(f"  [Converse] First token: {repr(text[:60])}")
                full_text += text

        elif "messageStop" in event:
            stop_reason = event["messageStop"].get("stopReason", "")
            print(f"  [Converse] Stop reason: {stop_reason}")
            if stop_reason == "guardrail_intervened":
                print(f"  [Converse] GUARDRAIL BLOCKED the response")

        elif "metadata" in event:
            usage = event["metadata"].get("usage", {})
            input_tokens = usage.get("inputTokens", 0)
            output_tokens = usage.get("outputTokens", 0)
            # Guardrail trace in metadata
            trace = event["metadata"].get("trace", {})
            if trace:
                guardrail_trace = trace.get("guardrail", {})
                if guardrail_trace:
                    action = guardrail_trace.get("inputAssessment", {})
                    guardrail_events.append(guardrail_trace)
                    print(f"  [Guardrail] trace: {list(guardrail_trace.keys())}")

    t_end = time.perf_counter()
    total_ms = (t_end - t_start) * 1000
    ttft_ms = (t_first_token - t_start) * 1000 if t_first_token else total_ms

    print(f"  [Converse] Total time: {format_ms(total_ms)}")
    print(f"  [Converse] Tokens: {input_tokens} in / {output_tokens} out")

    return {
        "ttft_ms": ttft_ms,
        "total_ms": total_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "full_text": full_text,
        "trace_events": [],
        "guardrail_events": guardrail_events,
        "session_id": "converse-direct",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run_case(session, case: dict) -> dict[str, Any]:
    bedrock_agent_runtime = session.client("bedrock-agent-runtime", region_name=REGION)
    bedrock_runtime = session.client("bedrock-runtime", region_name=REGION)

    print(f"\n{hr('═')}")
    print(f"  {case['id']}: {case['label']}")
    print(hr('═'))
    print(f"  Query: {case['query'][:120]}...")
    print(f"  Model: {case['model']}")
    print(f"  SLA:   TTFT <= {format_ms(case['sla_ttft_ms'])}, Total <= {format_ms(case['sla_total_ms'])}")

    results = {}

    # ── Step A: Pure retrieval latency (Vector KB) ──────────────────────────
    print(f"\n{hr('─')}")
    print("  STEP A: Pure KB retrieval — Vector (OpenSearch Serverless)")
    print(hr('─'))
    retrieval_result = test_kb_retrieve(bedrock_agent_runtime, case["query"], case["id"],
                                        kb_id=KB_ID, label="Vector KB")
    results["retrieval"] = retrieval_result

    # ── Step A2: GraphRAG retrieval ──────────────────────────────────────────
    print(f"\n{hr('─')}")
    print("  STEP A2: GraphRAG retrieval — Neptune Analytics (entity + relation traversal)")
    print(hr('─'))
    graphrag_result = test_kb_retrieve(bedrock_agent_runtime, case["query"], case["id"],
                                       kb_id=GRAPHRAG_KB_ID, label="GraphRAG KB") if GRAPHRAG_KB_ID else {"retrieval_ms": 0, "num_chunks": 0, "chunks": []}
    results["graphrag"] = graphrag_result

    # Merge chunks from both KBs for generation context
    all_chunks = retrieval_result["chunks"] + graphrag_result["chunks"]

    # ── Step B: RetrieveAndGenerate (simpler, no agent overhead) ────────────
    print(f"\n{hr('─')}")
    print("  STEP B: RetrieveAndGenerate (KB + model, no agent)")
    print(hr('─'))
    rag_result = test_retrieve_and_generate(bedrock_agent_runtime, case)
    results["rag"] = rag_result

    # ── Step C: Converse streaming with Guardrails ───────────────────────────
    print(f"\n{hr('─')}")
    print("  STEP C: Converse streaming + Guardrails (Vector + GraphRAG context, measures TTFT)")
    print(hr('─'))
    agent_result = test_converse_streaming(bedrock_runtime, case, all_chunks)
    results["agent"] = agent_result

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{hr('─')}")
    print(f"  RESULTS SUMMARY — {case['id']}")
    print(hr('─'))

    print(f"\n  Retrieval only (Vector KB):")
    print(f"    Latency:       {format_ms(retrieval_result['retrieval_ms'])}")
    print(f"    Chunks:        {retrieval_result['num_chunks']}")

    print(f"\n  GraphRAG retrieval (Neptune Analytics):")
    print(f"    Latency:       {format_ms(graphrag_result['retrieval_ms'])}")
    print(f"    Chunks:        {graphrag_result['num_chunks']}")
    print(f"    Total context: {len(all_chunks)} chunks (vector + graph)")

    print(f"\n  RetrieveAndGenerate (no agent):")
    print(f"    Total time:    {format_ms(rag_result['total_ms'])}")
    print(f"    Citations:     {rag_result['num_citations']}")
    print(f"    Refs:          {rag_result['num_refs']}")

    print(f"\n  Full Agent (Converse + Guardrails):")
    print(f"    TTFT:          {format_ms(agent_result['ttft_ms'])}")
    print(f"    Total time:    {format_ms(agent_result['total_ms'])}")
    print(f"    Input tokens:  {agent_result['input_tokens']}")
    print(f"    Output tokens: {agent_result['output_tokens']}")
    print(f"    Guardrail:     {len(agent_result['guardrail_events'])} events")
    print(f"    Citations:     {len(agent_result['trace_events'])} refs")

    # SLA check
    ttft_ok = agent_result["ttft_ms"] <= case["sla_ttft_ms"]
    total_ok = agent_result["total_ms"] <= case["sla_total_ms"]
    print(f"\n  SLA check:")
    print(f"    TTFT  {format_ms(agent_result['ttft_ms'])} <= {format_ms(case['sla_ttft_ms'])}: {'PASS' if ttft_ok else 'FAIL'}")
    print(f"    Total {format_ms(agent_result['total_ms'])} <= {format_ms(case['sla_total_ms'])}: {'PASS' if total_ok else 'FAIL'}")

    # Keyword check
    kw_results = check_keywords(
        rag_result["output_text"] + agent_result["full_text"],
        case["expected_keywords"]
    )
    print(f"\n  Keyword coverage:")
    for kw, found in kw_results.items():
        print(f"    {'[x]' if found else '[ ]'} {kw}")

    # Print answer
    print(f"\n  Answer (RetrieveAndGenerate):")
    print(f"  {hr()}")
    answer = rag_result["output_text"]
    for line in answer.split("\n"):
        print(f"  {line}")

    print(f"\n  Answer (Agent):")
    print(f"  {hr()}")
    agent_answer = agent_result["full_text"]
    for line in agent_answer.split("\n"):
        print(f"  {line}")

    return results


def main():
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)

    print(hr('═', 72))
    print("  Nova Health Tech — Managed Stack Test")
    print(f"  KB: {KB_ID}  |  Agent: {AGENT_ID}  |  Guardrail: {GUARDRAIL_ID}")
    print(hr('═', 72))

    all_results = {}
    for case in CASES:
        result = run_case(session, case)
        all_results[case["id"]] = result

    # Final comparison table
    print(f"\n{hr('═', 72)}")
    print("  FINAL COMPARISON")
    print(hr('═', 72))
    print(f"\n  {'Metric':<35} {'CASE-1 Emergency':<22} {'CASE-2 Complex'}")
    print(f"  {hr('-', 70)}")

    metrics = [
        ("Retrieval latency", "retrieval.retrieval_ms", "ms"),
        ("Retrieval chunks", "retrieval.num_chunks", ""),
        ("RAG total time", "rag.total_ms", "ms"),
        ("Agent TTFT", "agent.ttft_ms", "ms"),
        ("Agent total time", "agent.total_ms", "ms"),
        ("Input tokens", "agent.input_tokens", ""),
        ("Output tokens", "agent.output_tokens", ""),
    ]

    def get_val(results, path):
        parts = path.split(".")
        v = results
        for p in parts:
            v = v.get(p, 0)
        return v

    for label, path, unit in metrics:
        v1 = get_val(all_results.get("CASE-1-EMERGENCY", {}), path)
        v2 = get_val(all_results.get("CASE-2-COMPLEX", {}), path)
        if unit == "ms":
            s1 = format_ms(v1)
            s2 = format_ms(v2)
        else:
            s1 = str(v1)
            s2 = str(v2)
        print(f"  {label:<35} {s1:<22} {s2}")

    print(f"\n  SLA targets:")
    print(f"  {'Emergency TTFT':<35} <= 2 s")
    print(f"  {'Complex TTFT':<35} <= 4 s")
    print(f"  {'Emergency total':<35} <= 5 s")
    print(f"  {'Complex total':<35} <= 15 s")

    # Save results
    out = Path(__file__).parent / ".test_results.json"
    # Convert to serializable
    def clean(obj):
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(i) for i in obj]
        if isinstance(obj, float):
            return round(obj, 2)
        return obj
    out.write_text(json.dumps(clean(all_results), indent=2), encoding="utf-8")
    print(f"\n  Full results saved to {out}")


if __name__ == "__main__":
    main()
