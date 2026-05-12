import boto3

session = boto3.Session(profile_name="gapv50k", region_name="ap-southeast-1")
client = session.client("bedrock-agent-runtime")

docs = [
    "Dexamethasone 6mg daily for severe COVID-19 per WHO guidelines",
    "Remdesivir 200mg loading dose for non-severe high-risk COVID-19",
    "Baricitinib 4mg for severe or critical COVID-19",
    "Prophylactic heparin for hospitalized COVID-19 patients",
    "Tocilizumab 8mg/kg IV for severe COVID-19",
]

query = "dexamethasone dose severe COVID-19"

# Test Cohere Rerank v3.5
print("=== Cohere Rerank v3.5 ===")
try:
    resp = client.rerank(
        queries=[{"type": "TEXT", "textQuery": {"text": query}}],
        sources=[
            {"type": "INLINE", "inlineDocumentSource": {"type": "TEXT", "textDocument": {"text": d}}}
            for d in docs
        ],
        rerankingConfiguration={
            "type": "BEDROCK_RERANKING_MODEL",
            "bedrockRerankingConfiguration": {
                "numberOfResults": 3,
                "modelConfiguration": {
                    "modelArn": "arn:aws:bedrock:ap-southeast-1::foundation-model/cohere.rerank-v3-5:0"
                },
            },
        },
    )
    print("WORKS in ap-southeast-1!")
    for r in resp["results"]:
        idx = r["index"]
        score = r["relevanceScore"]
        print(f"  [{idx}] score={score:.4f}  {docs[idx][:60]}")
except Exception as e:
    print(f"FAILED: {e}")

# Test Amazon Rerank v1
print("\n=== Amazon Rerank v1 ===")
try:
    resp2 = client.rerank(
        queries=[{"type": "TEXT", "textQuery": {"text": query}}],
        sources=[
            {"type": "INLINE", "inlineDocumentSource": {"type": "TEXT", "textDocument": {"text": d}}}
            for d in docs
        ],
        rerankingConfiguration={
            "type": "BEDROCK_RERANKING_MODEL",
            "bedrockRerankingConfiguration": {
                "numberOfResults": 3,
                "modelConfiguration": {
                    "modelArn": "arn:aws:bedrock:ap-southeast-1::foundation-model/amazon.rerank-v1:0"
                },
            },
        },
    )
    print("WORKS in ap-southeast-1!")
    for r in resp2["results"]:
        idx = r["index"]
        score = r["relevanceScore"]
        print(f"  [{idx}] score={score:.4f}  {docs[idx][:60]}")
except Exception as e:
    print(f"FAILED: {e}")
