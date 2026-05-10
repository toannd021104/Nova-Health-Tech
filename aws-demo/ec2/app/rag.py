"""Build + query the FAISS retrieval index from the S3 corpus.

We load every object under s3://$S3_BUCKET/$KB_PREFIX/, extract text (PDFs via
pypdf, JSON via native parse), chunk, embed with Titan v2, and persist a FAISS
index under /opt/nova/faiss/.  On cold start we rebuild once; subsequent
restarts reuse the persisted index.
"""
from __future__ import annotations

import io
import json
import os
import logging
from pathlib import Path
from typing import Iterable

import boto3
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

log = logging.getLogger("rag")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
S3_BUCKET = os.environ["S3_BUCKET"]
KB_PREFIX = os.environ.get("KB_PREFIX", "kb-src").strip("/")
EMBED_MODEL_ID = os.environ.get("EMBED_MODEL_ID", "global.cohere.embed-v4:0")
INDEX_DIR = Path(os.environ.get("FAISS_DIR", "/opt/nova/faiss"))

_vectorstore: FAISS | None = None


def _s3():
    return boto3.client("s3", region_name=REGION)


class CohereBedrockEmbeddings(Embeddings):
    """Minimal LangChain Embeddings wrapper for Cohere Embed v4 on Bedrock.

    Cohere's Bedrock API requires distinct `input_type` values for documents
    vs queries, which langchain-aws's generic BedrockEmbeddings doesn't expose
    cleanly. We batch up to 96 texts per request (Cohere's limit).
    """

    def __init__(self, model_id: str = EMBED_MODEL_ID, region_name: str = REGION):
        self.model_id = model_id
        self.region_name = region_name
        self._client = boto3.client("bedrock-runtime", region_name=region_name)

    def _embed(self, texts: list[str], input_type: str) -> list[list[float]]:
        out: list[list[float]] = []
        batch = 96
        for i in range(0, len(texts), batch):
            part = texts[i : i + batch]
            resp = self._client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({"texts": part, "input_type": input_type}),
                contentType="application/json",
                accept="application/json",
            )
            data = json.loads(resp["body"].read())
            out.extend(data["embeddings"]["float"])
        return out

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, input_type="search_document")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], input_type="search_query")[0]


def _bedrock_embeddings() -> CohereBedrockEmbeddings:
    return CohereBedrockEmbeddings()


def _iter_s3_keys() -> Iterable[str]:
    s3 = _s3()
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=f"{KB_PREFIX}/"):
        for obj in page.get("Contents", []):
            yield obj["Key"]


def _read_pdf(body: bytes, source: str) -> list[Document]:
    reader = PdfReader(io.BytesIO(body))
    docs: list[Document] = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            log.warning("pdf extract failed on %s page %d: %s", source, i, exc)
            continue
        text = text.strip()
        if not text:
            continue
        docs.append(
            Document(
                page_content=text,
                metadata={"source": source, "page": i + 1, "type": "pdf"},
            )
        )
    return docs


def _read_json(body: bytes, source: str) -> list[Document]:
    try:
        data = json.loads(body.decode("utf-8"))
    except Exception as exc:
        log.warning("json parse failed on %s: %s", source, exc)
        return []

    if isinstance(data, dict) and data.get("@id"):
        parts: list[str] = []
        title = (data.get("title") or {}).get("@value") or (data.get("code") or "")
        parts.append(f"ICD-11 {title}")
        if definition := (data.get("definition") or {}).get("@value"):
            parts.append(f"Definition: {definition}")
        if inclusions := data.get("inclusion"):
            inc_labels = [
                (i.get("label") or {}).get("@value") for i in inclusions if isinstance(i, dict)
            ]
            inc_labels = [x for x in inc_labels if x]
            if inc_labels:
                parts.append("Inclusions: " + "; ".join(inc_labels))
        if exclusions := data.get("exclusion"):
            exc_labels = [
                (e.get("label") or {}).get("@value") for e in exclusions if isinstance(e, dict)
            ]
            exc_labels = [x for x in exc_labels if x]
            if exc_labels:
                parts.append("Exclusions: " + "; ".join(exc_labels))
        if code := data.get("code"):
            parts.append(f"Code: {code}")
        return [
            Document(
                page_content="\n".join(parts),
                metadata={
                    "source": source,
                    "type": "icd11-entity",
                    "icd11_id": data.get("@id", ""),
                },
            )
        ]

    # generic JSON fallback — just stringify
    return [Document(page_content=json.dumps(data)[:8000], metadata={"source": source, "type": "json"})]


def _load_documents() -> list[Document]:
    s3 = _s3()
    docs: list[Document] = []
    for key in _iter_s3_keys():
        body = s3.get_object(Bucket=S3_BUCKET, Key=key)["Body"].read()
        source = f"s3://{S3_BUCKET}/{key}"
        if key.lower().endswith(".pdf"):
            docs.extend(_read_pdf(body, source))
        elif key.lower().endswith(".json"):
            docs.extend(_read_json(body, source))
        else:
            log.info("skipping unsupported file %s", key)
    log.info("loaded %d source documents from S3", len(docs))
    return docs


def build_or_load() -> FAISS:
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    embeddings = _bedrock_embeddings()
    index_path = INDEX_DIR / "index.faiss"

    if index_path.exists():
        log.info("loading existing FAISS index from %s", INDEX_DIR)
        _vectorstore = FAISS.load_local(
            str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True
        )
        return _vectorstore

    log.info("building fresh FAISS index; this can take a minute")
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    raw = _load_documents()
    if not raw:
        raise RuntimeError(f"no documents found under s3://{S3_BUCKET}/{KB_PREFIX}/")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=120, separators=["\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_documents(raw)
    log.info("chunked %d raw docs into %d chunks", len(raw), len(chunks))

    _vectorstore = FAISS.from_documents(chunks, embeddings)
    _vectorstore.save_local(str(INDEX_DIR))
    log.info("FAISS index saved to %s (%d chunks)", INDEX_DIR, len(chunks))
    return _vectorstore


def retriever(k: int = 4):
    return build_or_load().as_retriever(search_kwargs={"k": k})
