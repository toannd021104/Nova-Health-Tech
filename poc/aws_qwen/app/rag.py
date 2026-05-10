"""RAG for the POC — OpenSearch Serverless hybrid retrieval + Amazon Rerank.

Embeddings and reranking are done with **Amazon-native models on Bedrock**
(no Cohere):

- **Amazon Titan Embed Text v2** (`amazon.titan-embed-text-v2:0`) for text
  chunk embeddings. Available in Singapore (`ap-southeast-1`). 1024-dim,
  $0.02 per 1M tokens — cheaper than Cohere Embed v4.

- **Amazon Rerank 1.0** (`amazon.rerank-v1:0`) for post-retrieval reranking.
  Only hosted in Tokyo (`ap-northeast-1`) and Oregon (`us-west-2`), so the
  Lambda makes a cross-region call to Tokyo from Singapore (~70 ms RTT, fine
  for the complex lane).

On the complex lane we retrieve the top-20 by vector similarity, then rerank
down to the top-5 before giving them to the specialist agent.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Iterable

import boto3
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

log = logging.getLogger(__name__)

# Model IDs — Amazon-only, no Cohere.
TITAN_EMBED = "amazon.titan-embed-text-v2:0"
AMAZON_RERANK = "amazon.rerank-v1:0"

# Regions
SG_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
RERANK_REGION = os.environ.get("RERANK_REGION", "ap-northeast-1")  # Amazon Rerank is Tokyo or Oregon only

FAISS_DIR = Path(os.environ.get("FAISS_DIR", "/tmp/nova-faiss"))


class TitanBedrockEmbeddings(Embeddings):
    """LangChain wrapper around Amazon Titan Embed Text v2 on Bedrock."""

    def __init__(self, model_id: str = TITAN_EMBED, *, bedrock=None):
        self._model = model_id
        self._bedrock = bedrock or boto3.client("bedrock-runtime", region_name=SG_REGION)

    def embed_query(self, text: str) -> list[float]:
        return self._embed_one(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Titan Embed v2 takes one input per call. For higher throughput,
        # batch at the orchestrator level; for the POC this is plenty.
        return [self._embed_one(t) for t in texts]

    def _embed_one(self, text: str) -> list[float]:
        payload = {"inputText": text, "dimensions": 1024, "normalize": True}
        resp = self._bedrock.invoke_model(
            modelId=self._model,
            body=json.dumps(payload),
            contentType="application/json",
        )
        body = json.loads(resp["body"].read())
        return body["embedding"]


# Per-namespace in-memory FAISS stores, loaded lazily from disk.
_STORES: dict[str, FAISS] = {}


def _load_namespace(namespace: str) -> FAISS:
    if namespace in _STORES:
        return _STORES[namespace]
    ns_path = FAISS_DIR / namespace
    if not ns_path.exists():
        raise FileNotFoundError(f"FAISS index not found for namespace: {namespace}")
    embeddings = TitanBedrockEmbeddings()
    store = FAISS.load_local(str(ns_path), embeddings, allow_dangerous_deserialization=True)
    _STORES[namespace] = store
    return store


def retrieve(query: str, namespace: str, top_k: int = 5, *, rerank: bool = True) -> list[dict]:
    """Hybrid-ish retrieval: FAISS vector top-20 → Amazon Rerank top-5.

    FAISS gives us dense-vector recall; we compensate for the absence of BM25
    (which OpenSearch Serverless provides in production) by overshooting k
    and applying a stronger reranker.
    """
    store = _load_namespace(namespace)
    overshoot = 20 if rerank else top_k
    raw_hits = store.similarity_search(query, k=overshoot)

    if not rerank or len(raw_hits) <= top_k:
        hits = raw_hits[:top_k]
    else:
        hits = _amazon_rerank(query, raw_hits, top_k)

    return [
        {
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page"),
            "text": doc.page_content,
            "score": doc.metadata.get("rerank_score"),
        }
        for doc in hits
    ]


def _amazon_rerank(query: str, docs: list[Document], top_k: int) -> list[Document]:
    """Call Amazon Rerank 1.0 (cross-region to Tokyo) to re-score the candidates."""
    client = boto3.client("bedrock-agent-runtime", region_name=RERANK_REGION)
    try:
        resp = client.rerank(
            queries=[{"type": "TEXT", "textQuery": {"text": query}}],
            sources=[
                {
                    "type": "INLINE",
                    "inlineDocumentSource": {
                        "type": "TEXT",
                        "textDocument": {"text": d.page_content[:5000]},
                    },
                }
                for d in docs
            ],
            rerankingConfiguration={
                "type": "BEDROCK_RERANKING_MODEL",
                "bedrockRerankingConfiguration": {
                    "numberOfResults": top_k,
                    "modelConfiguration": {
                        "modelArn": (
                            f"arn:aws:bedrock:{RERANK_REGION}::foundation-model/{AMAZON_RERANK}"
                        ),
                    },
                },
            },
        )
    except Exception as exc:  # noqa: BLE001
        log.warning("Amazon Rerank failed (%s); falling back to raw order", exc)
        return docs[:top_k]

    # Results come back as a list of {index, relevanceScore} tuples referring
    # to the original source order.
    ordered: list[Document] = []
    for result in resp.get("results", []):
        idx = result.get("index")
        score = result.get("relevanceScore")
        if idx is not None and 0 <= idx < len(docs):
            doc = docs[idx]
            doc.metadata["rerank_score"] = score
            ordered.append(doc)
    return ordered or docs[:top_k]


# --- Ingestion (run once at deploy time) -------------------------------------


def _iter_pdf_chunks(
    pdf_path: Path, *, chunk_size: int = 1500, overlap: int = 300
) -> Iterable[Document]:
    reader = PdfReader(str(pdf_path))
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if not text.strip():
            continue
        for piece in splitter.split_text(text):
            yield Document(
                page_content=piece,
                metadata={"source": pdf_path.name, "page": page_num},
            )


def _iter_json_chunks(json_path: Path) -> Iterable[Document]:
    """Treat each ICD-11 entity JSON file as one document."""
    try:
        obj = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        log.warning("skip %s: %s", json_path, exc)
        return
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    yield Document(page_content=text, metadata={"source": json_path.name})


def build_namespace(namespace: str, input_dir: Path) -> Path:
    """Build a FAISS index for a namespace from a folder of PDFs / JSON files."""
    embeddings = TitanBedrockEmbeddings()
    docs: list[Document] = []
    for path in sorted(input_dir.rglob("*")):
        if path.suffix.lower() == ".pdf":
            docs.extend(_iter_pdf_chunks(path))
        elif path.suffix.lower() == ".json":
            docs.extend(_iter_json_chunks(path))
    if not docs:
        log.warning("no documents found in %s", input_dir)
        return FAISS_DIR / namespace
    log.info(
        "namespace=%s docs=%d chunks=%d",
        namespace,
        len({d.metadata.get("source") for d in docs}),
        len(docs),
    )
    store = FAISS.from_documents(docs, embeddings)
    out = FAISS_DIR / namespace
    out.mkdir(parents=True, exist_ok=True)
    store.save_local(str(out))
    return out
