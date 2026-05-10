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

### Concrete AWS implementation

- **Parser**: Amazon Bedrock Data Automation (BDA) in advanced-parsing mode.
- **Chunking**: Bedrock Knowledge Bases hierarchical chunking (parent 1500 tokens, child 300 tokens, 15% overlap). Parent chunks give the LLM enough context; child chunks drive precise retrieval.
- **Embeddings**: Amazon Titan Embed Text v2 for text chunks; Amazon Nova Multimodal Embeddings for any chunk that contains a figure reference (embedding both text and cropped figure into one vector).
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
- [WHO ICD-11 API Swagger](https://id.who.int/swagger/index.html)

*Content above is rephrased for compliance with licensing restrictions.*
