"""GraphRAG — Bedrock Knowledge Bases GraphRAG on Neptune Analytics.

Reuses the same GraphRAG KB as aws_claude:
  KB ID:   FU6SXD0B8B  (Neptune Analytics g-0keuwoev4a)
  Region:  ap-southeast-1 Singapore

Retrieval uses SEMANTIC search (HYBRID not supported for Neptune-backed KBs).
Same behaviour as aws_claude graphrag.py.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

import boto3

log = logging.getLogger(__name__)

REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
GRAPHRAG_KB_ID = os.environ.get("BEDROCK_GRAPHRAG_KB_ID", "FU6SXD0B8B")  # same as aws_claude

_GRAPHRAG_CLIENT = None


def _get_graphrag_client():
    global _GRAPHRAG_CLIENT
    if _GRAPHRAG_CLIENT is None:
        _GRAPHRAG_CLIENT = boto3.client("bedrock-agent-runtime", region_name=REGION)
    return _GRAPHRAG_CLIENT


@dataclass
class GraphHit:
    text: str
    source: str
    score: float


def graph_retrieve(query: str, top_k: int = 5) -> list[GraphHit]:
    """Retrieve from Bedrock GraphRAG KB (Neptune Analytics, Singapore)."""
    if not GRAPHRAG_KB_ID:
        log.info("graph_retrieve: BEDROCK_GRAPHRAG_KB_ID not set; returning empty")
        return []

    client = _get_graphrag_client()
    try:
        resp = client.retrieve(
            knowledgeBaseId=GRAPHRAG_KB_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": top_k,
                    "overrideSearchType": "SEMANTIC",  # HYBRID not supported for Neptune KB
                }
            },
        )
    except Exception as exc:  # noqa: BLE001
        log.warning("GraphRAG retrieve failed: %s", exc)
        return []

    hits: list[GraphHit] = []
    for r in resp.get("retrievalResults", []):
        text = r.get("content", {}).get("text", "")
        source = r.get("location", {}).get("s3Location", {}).get("uri", "graph")
        score = r.get("score", 0.0)
        hits.append(GraphHit(text=text, source=source, score=score))
    return hits
