#!/usr/bin/env bash
# Download the MedRAG PubMed sample chunk (15,377 abstracts, ~32 MB).
# Used as the "external literature" corpus for the RAG pipeline.
#
# Usage: bash scripts/download_medrag_pubmed.sh
set -euo pipefail

OUT_DIR="data/pubmed"
OUT_FILE="${OUT_DIR}/pubmed_medrag_sample.jsonl"
URL="https://huggingface.co/datasets/MedRAG/pubmed/resolve/main/chunk/pubmed23n0001.jsonl"

mkdir -p "${OUT_DIR}"
echo "Downloading MedRAG PubMed chunk → ${OUT_FILE}"
curl -sS -L -A "Mozilla/5.0 NovaHealth-RAG/1.0" "${URL}" -o "${OUT_FILE}"
echo "Done. Size: $(wc -c < "${OUT_FILE}") bytes, lines: $(wc -l < "${OUT_FILE}")"
