"""RAG for the POC — Bedrock Knowledge Bases hybrid retrieval.

Uses the deployed Vector KB (OpenSearch Serverless, MUEEBGPRSJ) via
Bedrock KB Retrieve API. Embedding is handled by Bedrock KB internally
using Cohere Embed Multilingual v3 (SG-native).

Amazon Rerank 1.0 is NOT available in ap-southeast-1. We skip reranking
and return the top-k directly from the KB. This is a known gap vs the
production proposal.

No FAISS, no Titan Embed, no cross-region calls.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from typing import Any

import boto3

log = logging.getLogger(__name__)

REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
KB_ID = os.environ.get("BEDROCK_KB_ID", "MUEEBGPRSJ")

_KB_CLIENT = None


def _get_kb_client():
    global _KB_CLIENT
    if _KB_CLIENT is None:
        _KB_CLIENT = boto3.client("bedrock-agent-runtime", region_name=REGION)
    return _KB_CLIENT


def retrieve(query: str, namespace: str = "", top_k: int = 15, **_) -> list[dict[str, Any]]:
    """Retrieve from Bedrock Vector KB (OpenSearch Serverless).

    `namespace` is accepted for API compatibility with the old FAISS path
    but is not used — the KB covers all departments.

    Returns top-15 results by default for better recall across diverse data sources.
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


def bootstrap_from_s3(**_) -> dict[str, int]:
    """No-op — Bedrock KB handles indexing; no local FAISS bootstrap needed."""
    log.info("bootstrap_from_s3: using Bedrock KB, no local index to build")
    return {"kb_id": KB_ID, "state": "bedrock_kb"}
