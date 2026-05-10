# RAG Strategy for Nova Health Tech — Complex Medical PDFs

## Problem

- Hundreds of WHO guideline PDFs, internal clinical trial reports, and treatment protocols.
- Each WHO guideline is 100+ pages of mixed **body text**, **tables (vertical and horizontal)**, **text-based graphs/flow charts**, and occasional **images/figures**.
- Internal trial reports have **inconsistent tagging** (heading styles, OCR quality, table format all vary).
- Plus the **structured WHO ICD-11 API** (see `scripts/download_who_icd.py`) for disease-level metadata.
- Freshness SLA: WHO publishes monthly updates that must land in the index within a day.

A naïve "PyPDF text extract → chunk → embed" pipeline fails on these documents. Tables become linearized garbage, horizontal tables split into rows that look like random sentences, and the text-only graphs (dosing flowcharts, decision trees) lose the structure that makes them clinically useful.

## Three candidate strategies, compared

### Strategy A — Fully managed parse + RAG (AWS Bedrock Data Automation; Alibaba DocMind + Qwen-VL)

The cloud provider's document-intelligence service converts the whole PDF into structured JSON (text blocks, tables as 2D arrays, figure descriptions, layout metadata), then Knowledge Bases (AWS) or Model Studio RAG Application (Ali) handle chunking, embedding and retrieval. One service, one dashboard, one IAM boundary.

Strengths: zero custom parsing code, strong table recognition, OCR built in, native handling of mixed layouts, PHI isolation via the same IAM policies as everything else.

Weaknesses: less control over chunking heuristics, per-page cost higher than open-source parsers, vendor lock-in, table-in-table or multi-page tables sometimes split across chunks.

### Strategy B — Open-source pipeline (Unstructured / LlamaParse / Docling) + self-managed vector DB

Self-hosted parser on container compute (ECS / ACK) writes structured JSON into S3/OSS, then a custom chunker + embedding + OpenSearch index. Gives you full control over chunking strategy per document type, and the parser can be swapped when a better one lands.

Strengths: cheapest per page, tunable per-doc-type (different chunker for a drug label vs a guideline), easy to add custom rules ("never split a dosing table"), reproducible.

Weaknesses: you own ops; each parser has weaknesses; keeping quality high across hundreds of heterogeneous PDFs takes engineering time; compliance review must cover your parser stack too.

### Strategy C — Multimodal embeddings of page-images (Amazon Nova Multimodal Embeddings on AWS; `tongyi-embedding-vision-plus` on Alibaba Singapore International, or `qwen3-vl-embedding` with `enable_fusion=True` if deploying in Chinese Mainland)

Skip parsing entirely. Render each PDF page to an image, embed the image + any extracted text together into a single vector. At query time, retrieve top-k pages as images and pass them directly to a vision-capable LLM (Claude Sonnet on AWS, Qwen-VL on Ali).

Strengths: preserves tables, graphs, and figures exactly as authored, no OCR errors, no chunking gymnastics, great for "show me the dosing flowchart" queries.

Weaknesses: higher embedding cost per page, larger input tokens per query (a page-image is expensive to process), response latency goes up, grounding/citations point at "page 42" rather than a specific paragraph.

## Recommendation

**Use Strategy A — fully managed parse + managed RAG — as the primary pipeline for both AWS and Alibaba versions**, with a **Strategy C fallback path** for documents where table/figure recall is critical (dosing flowcharts in particular).

Reasoning:

- WHO PDFs are the majority of the corpus and are professionally laid out. Bedrock Data Automation and Alibaba DocMind both handle these well out of the box. That means a two-week ramp instead of three months on a custom parser.
- Managed services keep the compliance boundary tight — Macie / SDDP scans and the cloud provider's BAA already cover them.
- The per-document cost is small next to what Nova will spend on LLM inference; optimizing parsing cost before the model is premature.
- Strategy C is available as a deterministic fallback for a short list of documents (typically < 10%) where tables or flowcharts matter and Strategy A misses them. The RAG router emits both a text chunk answer and, when the query matches a "needs the figure" classifier, a page-image answer.
- **Knowledge-Graph RAG is layered on top of Strategy A**, not a replacement. Both clouds expose managed GraphRAG services (Bedrock Knowledge Bases GraphRAG on Neptune Analytics for AWS; AnalyticDB for PostgreSQL GraphRAG service for Alibaba) that extract entities + relations from the same parsed corpus and expose a `graph_retrieve(entity, hops=2)` tool to the complex-lane agent. See §Graph-augmented retrieval below.

### Concrete AWS implementation

- **Parser**: Amazon Bedrock Data Automation (BDA) in advanced-parsing mode.
- **Chunking**: Bedrock Knowledge Bases hierarchical chunking (parent 1500 tokens, child 300 tokens, 15% overlap). Parent chunks give the LLM enough context; child chunks drive precise retrieval.
- **Embeddings**: Cohere Embed v4 on Bedrock (`global.cohere.embed-v4:0`, 1024-dim) for text chunks — matches the running demo in `aws-demo/ec2/app/rag.py`. Amazon Nova Multimodal Embeddings for figure-bearing chunks, stored in a **separate** vector field on the same document (the two embeddings live in different vector spaces, so retrieval runs two parallel kNN searches and merges at rerank time).
- **Vector store**: OpenSearch Serverless (vector collection) with HNSW + BM25 in the same index for hybrid retrieval.
- **Metadata** on every chunk: `source`, `document_id`, `document_type` ∈ {who-guideline, internal-trial, drug-label, icd11}, `publication_date`, `review_date`, `specialty`, `evidence_grade`, `page`, `section_heading`, `has_table`, `has_figure`.
- **Retrieval**: hybrid query, metadata pre-filter (default `review_date >= NOW-18m`), top-20 kNN, cross-encoder rerank (Cohere Rerank on Bedrock) to top-5, pass to the generation model.
- **Freshness**: EventBridge schedule on day 1 of each month → Step Functions → poll WHO guidelines page + ICD-11 API → upsert into S3 → Bedrock Knowledge Base sync job (incremental; only changed docs).

### Concrete Alibaba implementation

- **Parser**: DocMind for general PDFs; Qwen-VL-Max as a fallback on pages with complex tables or figures.
- **Chunking**: same hierarchical strategy (1500 / 300 tokens, 15% overlap), implemented in Function Compute.
- **Embeddings**: `text-embedding-v4` for text ($0.07 / 1M tokens, dims 64–2048). For figure-bearing chunks, `tongyi-embedding-vision-plus` (1152-dim; text + image + video; text priced at $0.09 / 1M tokens, media metered per input). Note: `qwen3-vl-embedding` with `enable_fusion=True` that `askAli_AI_Assistant.txt` originally recommended is **Chinese Mainland only** — it is not exposed on the Singapore International endpoint. Picking `tongyi-embedding-vision-plus` keeps the Singapore data-residency posture intact at the cost of text and image modalities being embedded into separate vectors rather than one fused vector.
- **Reranker**: `qwen3-rerank` ($0.1 / 1M tokens, 500-doc cap) before generation. `qwen3-vl-rerank` (multimodal) and `gte-rerank-v2` are not available on Singapore International.
- **Vector store**: OpenSearch Vector Search Edition — native integration with Model Studio embedding plugin handles re-vectorization on document upload.
- **Retrieval**: Model Studio RAG Application for retrieval; ranker node calls `qwen3-rerank` before generation.
- **Freshness**: CloudOps Scheduler cron (day 1) → Function Workflow → same refresh job → OSS upsert → Model Studio RAG re-index.

## Graph-augmented retrieval — managed GraphRAG service on top

Both clouds now ship a **managed** Graph-RAG service that sits beside the vector KB and draws from the same parsed corpus:

| Cloud | Service | How it wires in |
|---|---|---|
| **AWS** | **Amazon Bedrock Knowledge Bases GraphRAG on Amazon Neptune Analytics** (GA March 2025) | Bedrock KB automatically extracts entities and relations from the same documents fed to the vector KB, stores the graph in a Neptune Analytics graph, and exposes graph-aware retrieval through the same KB API. No Neo4j to run. |
| **Alibaba** | **AnalyticDB for PostgreSQL GraphRAG service** | Managed entity+relation extraction pipeline that reuses the RAG service's ingestion; graph is stored in ADBPG alongside the vector table; queried over the same OpenAPI. |

Why we put this at launch, not "maybe later":

- The complex lane already has questions that want graph traversal ("patients on warfarin with a history of AFib who also take amiodarone — what's the interaction story?"). Vector search alone answers poorly; the agent needs to walk entity relations.
- Global-scope questions ("summarize the common failure modes across the last 12 months of WHO sepsis updates") are exactly what community-summary graph retrieval is designed for.
- Both services handle entity extraction automatically — **no manual KG construction**. That removes the main complexity objection against GraphRAG.
- Self-hosted alternatives (Microsoft GraphRAG, LightRAG, LazyGraphRAG) stay on the shelf only for on-prem (Apsara Stack) deployments where the managed service can't run.

### Graph retrieval as a tool the agent picks

The complex-lane agent sees two retrieval tools, not one:

```python
def kb_retrieve(topic, source, max_age_days):
    """Hybrid BM25 + kNN over the vector KB. Use for direct factual
    lookup and most clinical answers."""

def graph_retrieve(entity, relation=None, hops=2):
    """Managed GraphRAG. Use when the question needs multi-hop traversal
    (drug-drug, condition-drug, trial-endpoint-cohort relationships) or
    a corpus-wide summary."""
```

The agent's router prompt lists a decision rubric: single-hop factual → kb_retrieve; multi-hop / relational / "summarize across" → graph_retrieve. Results from both land in the same citation frame, so every answer still has its `[N]` pointers back to concrete chunks.

### Freshness

Graph re-index runs on the same triggers as the vector KB sync: monthly WHO refresh, SharePoint webhook, daily ICD-11 delta. Both managed services do **incremental** updates, so we don't pay to re-extract entities for unchanged documents.

## ICD-11 API is a first-class source (not a single download)

This API is **the** "structured external source" the scenario mentions, alongside PubMed. It's used three ways:

1. **Ingest snapshot** — monthly walk (see `scripts/download_who_icd.py --walk --max-depth 2`) writes one JSON file per entity into `s3://nova-raw/icd11/entities/` / `oss://nova-raw/icd11/entities/`. Each file is chunked to one record per entity (definition, inclusions, exclusions, synonyms, coded parents) and indexed with `source=icd11`.
2. **Runtime tool call** — the Bedrock Agent (AWS) or Model Studio Application (Ali) exposes an `icd11_code(term)` tool that hits the live ICD-11 search endpoint, so a clinician asking "what's the ICD-11 code for puerperal sepsis?" gets the authoritative current answer without round-tripping the RAG index.
3. **Entity expansion at query time** — when a clinician's question contains a disease name, a lightweight classifier calls ICD-11 search to get synonyms and code, then adds those as boosted terms to the hybrid BM25 query → better recall.

See `docs/architecture/AWS_architecture.md` §4.2 and `docs/architecture/Alibaba_architecture.md` §4 for the wiring.

## References

- [Revolutionizing drug data analysis using Amazon Bedrock multimodal RAG capabilities](https://aws.amazon.com/blogs/machine-learning/revolutionizing-drug-data-analysis-using-amazon-bedrock-multimodal-rag-capabilities/)
- [Amazon Bedrock Knowledge Bases — advanced parsing, chunking, query reformulation](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-knowledge-bases-now-supports-advanced-parsing-chunking-and-query-reformulation-giving-greater-control-of-accuracy-in-rag-based-applications/)
- [Unlocking the value of unstructured data with Amazon Bedrock Data Automation](https://aws.amazon.com/blogs/industries/unlocking-the-value-of-unstructured-data-with-amazon-bedrock-data-automation/)
- [Document Parsing for RAG — A Complete Guide for 2026 (Omdena)](https://www.omdena.com/blog/document-parsing-for-rag)
- [RAG-based application on PAI for finance and healthcare (Alibaba)](https://www.alibabacloud.com/help/en/pai/use-cases/development-of-rag-application-flow)
- [Multimodal embeddings — Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/multimodal-embeddings)
- [AnalyticDB for PostgreSQL — GraphRAG service (Alibaba managed)](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service)
- [Amazon Bedrock Knowledge Bases GraphRAG on Neptune Analytics — GA announcement](https://aws.amazon.com/blogs/machine-learning/announcing-general-availability-of-amazon-bedrock-knowledge-bases-graphrag-with-amazon-neptune-analytics/)
- [Amazon Bedrock — build a knowledge base with Neptune Analytics graphs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-graphs.html)
- [WHO ICD-11 API Swagger](https://id.who.int/swagger/index.html)

*Content above is rephrased for compliance with licensing restrictions.*
