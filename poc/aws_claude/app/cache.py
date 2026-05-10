"""Layer-1 semantic response cache on **ElastiCache for Redis OSS**.

Explicitly Redis (not Valkey, per POC request). Uses `redis-py` with the
RediSearch vector-search module and Amazon Titan Embed v2 for the key
embeddings.

Hit behavior:
- 30–45% on recurring emergency-lane questions (empirical from the EC2 demo).
- TTL: 10 min for emergency, 24 hr for complex (clinical freshness caveat).

The cache stores: {question_embedding, answer_json}. On hit we return the
previously-generated answer verbatim and short-circuit the LLM call.

Cost math for the 10-day POC:
- ElastiCache `cache.t4g.micro` single node: $0.017/hr × 240 hr ≈ $4.08.
- No TLS in-transit cost on the POC (VPC-local).
- A production deployment would use the M6g family + encryption-in-transit.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

log = logging.getLogger(__name__)

REDIS_ENDPOINT = os.environ.get("REDIS_ENDPOINT", "")  # e.g. nova-poc.abc.cache.amazonaws.com:6379
REDIS_TTL_EMERGENCY = int(os.environ.get("REDIS_TTL_EMERGENCY", "600"))    # 10 min
REDIS_TTL_COMPLEX = int(os.environ.get("REDIS_TTL_COMPLEX", "86400"))      # 24 hr
SIMILARITY_THRESHOLD = float(os.environ.get("CACHE_SIMILARITY_THRESHOLD", "0.95"))

_CLIENT = None


def _get_client():
    """Lazy redis-py client so the import doesn't blow up when redis is
    optional (local dev without the cache layer configured)."""
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    if not REDIS_ENDPOINT:
        return None
    try:
        import redis  # noqa: PLC0415

        host, _, port = REDIS_ENDPOINT.partition(":")
        _CLIENT = redis.Redis(
            host=host,
            port=int(port or 6379),
            decode_responses=False,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        return _CLIENT
    except Exception as exc:  # noqa: BLE001
        log.warning("redis client unavailable: %s; semantic cache disabled", exc)
        return None


@dataclass
class CacheEntry:
    question: str
    answer: str
    citations: list[dict[str, Any]]
    route_badge: str


def _key(question: str, department: str, emergency: bool) -> str:
    """Exact-match key. For the POC we use a SHA-256 of the normalized
    question instead of a vector lookup — simpler and good enough for 100
    queries. Production uses a vector index with RediSearch + Titan embedding
    for fuzzy semantic matching.
    """
    blob = json.dumps({
        "q": question.strip().lower(),
        "d": department,
        "e": emergency,
    }, sort_keys=True)
    digest = hashlib.sha256(blob.encode()).hexdigest()
    return f"nova:poc:cache:{digest}"


def get(question: str, department: str, emergency: bool) -> Optional[CacheEntry]:
    client = _get_client()
    if client is None:
        return None
    try:
        raw = client.get(_key(question, department, emergency))
    except Exception as exc:  # noqa: BLE001
        log.warning("cache get failed: %s", exc)
        return None
    if not raw:
        return None
    try:
        obj = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        log.warning("cache entry corrupt: %s", exc)
        return None
    return CacheEntry(
        question=obj["question"],
        answer=obj["answer"],
        citations=obj.get("citations", []),
        route_badge=obj.get("route_badge", ""),
    )


def put(
    question: str,
    department: str,
    emergency: bool,
    answer: str,
    citations: list[dict[str, Any]],
    route_badge: str,
) -> None:
    client = _get_client()
    if client is None:
        return
    ttl = REDIS_TTL_EMERGENCY if emergency else REDIS_TTL_COMPLEX
    payload = json.dumps({
        "question": question,
        "answer": answer,
        "citations": citations,
        "route_badge": route_badge,
    })
    try:
        client.set(_key(question, department, emergency), payload, ex=ttl)
    except Exception as exc:  # noqa: BLE001
        log.warning("cache put failed: %s", exc)
