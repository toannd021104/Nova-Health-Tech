"""RAG for the PoC (Version B — AWS + Nova/Qwen student).

Reuses the same Bedrock Knowledge Base as aws_claude:
  KB ID:    MUEEBGPRSJ  (OpenSearch Serverless, Cohere Embed Multilingual v3)
  Region:   ap-southeast-1 Singapore

No FAISS, no Titan Embed, no cross-region calls.
Embedding is handled internally by Bedrock KB (Cohere Embed Multilingual v3).
Hybrid BM25 + kNN search via the KB Retrieve API.

GraphRAG KB (Neptune Analytics):
  KB ID:    FU6SXD0B8B
  Region:   ap-southeast-1 Singapore
  (handled in graphrag.py)
"""
from __future__ import annotations

import logging
import os
from typing import Any

import boto3

log = logging.getLogger(__name__)

REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
KB_ID = os.environ.get("BEDROCK_KB_ID", "MUEEBGPRSJ")   # same KB as aws_claude

_KB_CLIENT = None


def _get_kb_client():
    global _KB_CLIENT
    if _KB_CLIENT is None:
        _KB_CLIENT = boto3.client("bedrock-agent-runtime", region_name=REGION)
    return _KB_CLIENT


def retrieve(query: str, namespace: str = "", top_k: int = 15, **_) -> list[dict[str, Any]]:
    """Retrieve from Bedrock Vector KB (OpenSearch Serverless, hybrid BM25+kNN).

    `namespace` accepted for API compatibility but not used — the KB covers
    all departments. Same behaviour as aws_claude rag.py.
    """
    client = _get_kb_client()
    try:
        resp = client.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": top_k,
                    "overrideSearchType": "HYBRID",
                }
            },
        )
    except Exception as exc:  # noqa: BLE001
        log.warning("KB retrieve failed: %s", exc)
        return []

    results = []
    for r in resp.get("retrievalResults", []):
        text = r.get("content", {}).get("text", "")
        uri = r.get("location", {}).get("s3Location", {}).get("uri", "unknown")
        score = r.get("score", 0.0)
        results.append({
            "source": uri,
            "page": None,
            "text": text,
            "score": score,
        })
    return results
