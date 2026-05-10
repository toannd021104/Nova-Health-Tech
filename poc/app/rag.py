"""FAISS-based retrieval for the POC.

We build one FAISS index per department (cheap) and pick the namespace based
on the router decision. Embeddings are produced with Cohere Embed v4 on
Bedrock (same as the existing EC2 demo in aws-demo/ec2/app/rag.py).

The index is built once at deploy time (see poc/deploy.py) and loaded from
S3 on Lambda cold start. A warm container holds the indexes in memory.
"""
from __future__ import annotations

import io
import json
import logging
import os
from pathlib import Path
from typing import Iterable

import boto3
import numpy as np
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

log = logging.getLogger(__name__)

REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
EMBED_MODEL = os.environ.get("EMBED_MODEL_ID", "global.cohere.embed-v4:0")
FAISS_DIR = Path(os.environ.get("FAISS_DIR", "/tmp/nova-faiss"))


class CohereBedrockEmbeddings(Embeddings):
    """LangChain embedding wrapper around Bedrock Cohere Embed v4."""

    def __init__(self, model_id: str = EMBED_MODEL, *, bedrock=None):
        self._model = model_id
        self._bedrock = bedrock or boto3.client("bedrock-runtime", region_name=REGION)

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], input_type="search_query")[0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Cohere Embed v4 caps at 96 texts per request; chunk accordingly.
        out: list[list[float]] = []
        for i in range(0, len(texts), 96):
            batch = texts[i : i + 96]
            out.extend(self._embed(batch, input_type="search_document"))
        return out

    def _embed(self, texts: list[str], *, input_type: str) -> list[list[float]]:
        payload = {
            "texts": texts,
            "input_type": input_type,
            "embedding_types": ["float"],
        }
        resp = self._bedrock.invoke_model(
            modelId=self._model,
            body=json.dumps(payload),
            contentType="application/json",
        )
        body = json.loads(resp["body"].read())
        return body["embeddings"]["float"]


# Per-namespace in-memory cache of FAISS stores.
_STORES: dict[str, FAISS] = {}


def _load_namespace(namespace: str) -> FAISS:
    """Load a FAISS store from local disk (preloaded from S3 at cold start)."""
    if namespace in _STORES:
        return _STORES[namespace]
    ns_path = FAISS_DIR / namespace
    if not ns_path.exists():
        raise FileNotFoundError(f"FAISS index not found for namespace: {namespace}")
    embeddings = CohereBedrockEmbeddings()
    store = FAISS.load_local(str(ns_path), embeddings, allow_dangerous_deserialization=True)
    _STORES[namespace] = store
    return store


def retrieve(query: str, namespace: str, top_k: int = 5) -> list[dict]:
    """Return top-k chunks with source, page, and text."""
    store = _load_namespace(namespace)
    results = store.similarity_search(query, k=top_k)
    return [
        {
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page"),
            "text": doc.page_content,
        }
        for doc in results
    ]


# --- Ingestion (run once at deploy time) -------------------------------------


def _iter_pdf_chunks(pdf_path: Path, *, chunk_size: int = 1500, overlap: int = 300) -> Iterable[Document]:
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
    # Flatten the JSON to a readable string for embedding.
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    yield Document(page_content=text, metadata={"source": json_path.name})


def build_namespace(namespace: str, input_dir: Path) -> Path:
    """Build a FAISS index for a namespace from a folder of PDFs / JSON files."""
    embeddings = CohereBedrockEmbeddings()
    docs: list[Document] = []
    for path in sorted(input_dir.rglob("*")):
        if path.suffix.lower() == ".pdf":
            docs.extend(_iter_pdf_chunks(path))
        elif path.suffix.lower() == ".json":
            docs.extend(_iter_json_chunks(path))
    if not docs:
        log.warning("no documents found in %s", input_dir)
        return FAISS_DIR / namespace
    log.info("namespace=%s docs=%d chunks=%d", namespace, len(set(d.metadata.get("source") for d in docs)), len(docs))
    store = FAISS.from_documents(docs, embeddings)
    out = FAISS_DIR / namespace
    out.mkdir(parents=True, exist_ok=True)
    store.save_local(str(out))
    return out
