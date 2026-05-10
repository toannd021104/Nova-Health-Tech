"""GraphRAG — Amazon Bedrock Knowledge Bases GraphRAG on Neptune Analytics.

This module exposes a single `graph_retrieve(entity, hops=2)` tool that the
complex-lane agent can call when a question needs multi-hop traversal or a
corpus-wide summary. Bedrock KB GraphRAG:
  - extracts entities + relations from the same parsed corpus fed to the
    vector KB
  - stores the graph in Neptune Analytics (1 m-NCU minimum, $0.16/hr)
  - answers via a hybrid vector + graph traversal over the KB API

We call it via `bedrock-agent-runtime:Retrieve` with the GraphRAG-enabled
knowledge base ID. The graph is built once at deploy time (see
`poc/deploy.py`).
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import boto3

log = logging.getLogger(__name__)

KB_REGION = os.environ.get("KB_REGION", "ap-southeast-1")
KB_ID = os.environ.get("BEDROCK_KB_ID", "")  # set by poc/deploy.py


@dataclass
class GraphHit:
    text: str
    source: str
    score: float


def graph_retrieve(query: str, top_k: int = 5) -> list[GraphHit]:
    """Hybrid vector + graph retrieval via Bedrock KB GraphRAG.

    Returns empty list if KB_ID isn't configured (e.g. local dev without
    the graph service).
    """
    if not KB_ID:
        log.info("graph_retrieve called but KB_ID not set; returning empty")
        return []

    client = boto3.client("bedrock-agent-runtime", region_name=KB_REGION)
    try:
        resp = client.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": top_k,
                },
            },
        )
    except Exception as exc:  # noqa: BLE001
        log.warning("graph_retrieve failed: %s", exc)
        return []

    hits: list[GraphHit] = []
    for r in resp.get("retrievalResults", []):
        content = r.get("content", {}).get("text", "")
        source = (
            r.get("location", {})
            .get("s3Location", {})
            .get("uri", "graph")
        )
        hits.append(
            GraphHit(
                text=content,
                source=source,
                score=r.get("score", 0.0),
            )
        )
    return hits
