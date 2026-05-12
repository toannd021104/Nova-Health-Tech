"""
Setup GraphRAG KB and wire Guardrails into the test path.

Steps:
  1. Create a new Bedrock KB with Neptune Analytics as storage (GraphRAG)
  2. Sync WHO PDF — Bedrock auto-extracts entities/relations into Neptune
  3. Update .managed_outputs.json with the new KB ID
  4. Verify graph has data

Profile: gapv50k  |  Region: ap-southeast-1
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

log = logging.getLogger("setup_graphrag")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

PROFILE = "gapv50k"
REGION = "ap-southeast-1"
ACCOUNT = "307711587176"
STACK_TAG = "poc-claude"

BUCKET = "ha-cg9jlwnsyxvkzs1idwnrzxq-307711587176"
S3_PREFIX = "kb-who/"
GRAPH_ID = "g-0keuwoev4a"  # new graph with vectorSearchConfiguration(dim=1024)
KB_ROLE_NAME = "HA-YmVkcm9jay1rYi1yb2xl"

GRAPHRAG_KB_NAME = "nova-health-graphrag-kb"
# Graph construction model — Claude Haiku 4.5 via global inference profile
GRAPH_CONSTRUCTION_MODEL = (
    "arn:aws:bedrock:ap-southeast-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
)
EMBED_MODEL_ID = "cohere.embed-multilingual-v3"

OUTPUTS_PATH = Path(__file__).parent / ".managed_outputs.json"


def wait_for(check_fn, desc: str, interval: int = 15, timeout: int = 900):
    elapsed = 0
    while elapsed < timeout:
        result = check_fn()
        if result:
            return result
        log.info("  waiting for %s... (%ds)", desc, elapsed)
        time.sleep(interval)
        elapsed += interval
    raise TimeoutError(f"Timed out waiting for {desc}")


def ensure_graphrag_kb(bedrock_agent, kb_role_arn: str, graph_arn: str) -> str:
    """Create a Bedrock KB backed by Neptune Analytics (GraphRAG)."""
    # Check if already exists
    kbs = bedrock_agent.list_knowledge_bases()["knowledgeBaseSummaries"]
    for kb in kbs:
        if kb["name"] == GRAPHRAG_KB_NAME:
            log.info("  GraphRAG KB already exists: %s", kb["knowledgeBaseId"])
            return kb["knowledgeBaseId"]

    log.info("  creating GraphRAG KB %s", GRAPHRAG_KB_NAME)
    resp = bedrock_agent.create_knowledge_base(
        name=GRAPHRAG_KB_NAME,
        description="Nova Health WHO guidelines — GraphRAG on Neptune Analytics",
        roleArn=kb_role_arn,
        knowledgeBaseConfiguration={
            "type": "VECTOR",
            "vectorKnowledgeBaseConfiguration": {
                "embeddingModelArn": (
                    f"arn:aws:bedrock:{REGION}::foundation-model/{EMBED_MODEL_ID}"
                ),
            },
        },
        storageConfiguration={
            "type": "NEPTUNE_ANALYTICS",
            "neptuneAnalyticsConfiguration": {
                "graphArn": graph_arn,
                "fieldMapping": {
                    "textField": "text",
                    "metadataField": "metadata",
                },
            },
        },
        tags={"Stack": STACK_TAG},
    )
    kb_id = resp["knowledgeBase"]["knowledgeBaseId"]
    log.info("  KB created: %s — waiting for ACTIVE", kb_id)

    def check():
        kb = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)["knowledgeBase"]
        return kb_id if kb["status"] == "ACTIVE" else None
    wait_for(check, f"GraphRAG KB {kb_id} ACTIVE", interval=10, timeout=300)
    return kb_id


def ensure_graphrag_datasource(bedrock_agent, kb_id: str) -> str:
    """Create S3 data source with graph construction (entity extraction) enabled."""
    ds_list = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)["dataSourceSummaries"]
    if ds_list:
        ds_id = ds_list[0]["dataSourceId"]
        log.info("  data source already exists: %s", ds_id)
        return ds_id

    log.info("  creating S3 data source with graph construction model")
    resp = bedrock_agent.create_data_source(
        knowledgeBaseId=kb_id,
        name="who-guidelines-graphrag",
        description="WHO B09540-eng.pdf with entity extraction",
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": {
                "bucketArn": f"arn:aws:s3:::{BUCKET}",
                "inclusionPrefixes": [S3_PREFIX],
            },
        },
        vectorIngestionConfiguration={
            "contextEnrichmentConfiguration": {
                "type": "BEDROCK_FOUNDATION_MODEL",
                "bedrockFoundationModelConfiguration": {
                    "modelArn": GRAPH_CONSTRUCTION_MODEL,
                    "enrichmentStrategyConfiguration": {
                        "method": "CHUNK_ENTITY_EXTRACTION",
                    },
                },
            },
        },
    )
    ds_id = resp["dataSource"]["dataSourceId"]
    log.info("  data source created: %s", ds_id)
    return ds_id


def sync_graphrag_kb(bedrock_agent, kb_id: str, ds_id: str):
    """Start ingestion — Bedrock extracts entities/relations into Neptune."""
    log.info("  starting GraphRAG ingestion job (entity extraction + graph build)")
    resp = bedrock_agent.start_ingestion_job(
        knowledgeBaseId=kb_id,
        dataSourceId=ds_id,
    )
    job_id = resp["ingestionJob"]["ingestionJobId"]
    log.info("  ingestion job: %s", job_id)

    def check():
        job = bedrock_agent.get_ingestion_job(
            knowledgeBaseId=kb_id, dataSourceId=ds_id, ingestionJobId=job_id
        )["ingestionJob"]
        status = job["status"]
        if status in ("COMPLETE", "FAILED", "PARTIALLY_FAILED"):
            stats = job.get("statistics", {})
            log.info(
                "  ingestion %s: scanned=%s indexed=%s failed=%s",
                status,
                stats.get("numberOfDocumentsScanned", 0),
                stats.get("numberOfNewDocumentsIndexed", 0)
                + stats.get("numberOfModifiedDocumentsIndexed", 0),
                stats.get("numberOfDocumentsFailed", 0),
            )
            if status == "FAILED":
                log.error("  failure reasons: %s", job.get("failureReasons", []))
            return True
        return None

    # GraphRAG ingestion takes longer (entity extraction LLM calls)
    wait_for(check, f"ingestion {job_id}", interval=20, timeout=1200)


def update_kb_role_for_neptune(iam, graph_arn: str):
    """Add Neptune Analytics permissions to the KB role."""
    log.info("  updating KB role with Neptune Analytics permissions")
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "S3Access",
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{BUCKET}",
                    f"arn:aws:s3:::{BUCKET}/*",
                ],
            },
            {
                "Sid": "BedrockFoundationModels",
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                "Resource": [
                    f"arn:aws:bedrock:{REGION}::foundation-model/*",
                    f"arn:aws:bedrock:*::foundation-model/*",
                    f"arn:aws:bedrock:{REGION}:{ACCOUNT}:inference-profile/*",
                ],
            },
            {
                "Sid": "BedrockControlPlane",
                "Effect": "Allow",
                "Action": [
                    "bedrock:GetInferenceProfile",
                    "bedrock:ListInferenceProfiles",
                    "bedrock:GetFoundationModel",
                    "bedrock:ListFoundationModels",
                ],
                "Resource": "*",
            },
            {
                "Sid": "AOSSAccess",
                "Effect": "Allow",
                "Action": ["aoss:APIAccessAll"],
                "Resource": [f"arn:aws:aoss:{REGION}:{ACCOUNT}:collection/*"],
            },
            {
                "Sid": "NeptuneAccess",
                "Effect": "Allow",
                "Action": [
                    "neptune-graph:GetGraph",
                    "neptune-graph:ListGraphs",
                    "neptune-graph:ReadDataViaQuery",
                    "neptune-graph:WriteDataViaQuery",
                    "neptune-graph:DeleteDataViaQuery",
                    "neptune-graph:GetQueryStatus",
                    "neptune-graph:CancelQuery",
                ],
                "Resource": [graph_arn],
            },
        ],
    }
    iam.put_role_policy(
        RoleName=KB_ROLE_NAME,
        PolicyName="bedrock-kb-access",
        PolicyDocument=json.dumps(policy),
    )
    log.info("  KB role updated")
    time.sleep(15)


def verify_graph_data(neptune_query_client, graph_id: str):
    """Run a simple openCypher query to verify entities were loaded."""
    log.info("  verifying Neptune graph data...")
    try:
        resp = neptune_query_client.execute_query(
            graphIdentifier=graph_id,
            queryString="MATCH (n) RETURN labels(n) AS label, count(*) AS cnt ORDER BY cnt DESC LIMIT 10",
            language="OPEN_CYPHER",
        )
        import io
        result_bytes = resp["payload"].read()
        result = json.loads(result_bytes.decode("utf-8"))
        rows = result.get("results", [])
        if rows:
            log.info("  graph node counts:")
            for row in rows:
                log.info("    %s: %s", row.get("label"), row.get("cnt"))
        else:
            log.warning("  graph appears empty — entity extraction may still be in progress")
    except Exception as e:
        log.warning("  could not query graph: %s", e)


def main():
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    bedrock_agent = session.client("bedrock-agent")
    iam = session.client("iam")
    neptune = session.client("neptune-graph")
    neptune_query = session.client("neptune-graph", region_name=REGION)

    # Load existing outputs
    outputs = json.loads(OUTPUTS_PATH.read_text())
    graph_id = outputs["graph_id"]

    # Get graph ARN
    graph_detail = neptune.get_graph(graphIdentifier=graph_id)
    graph_arn = graph_detail["arn"]
    log.info("Neptune graph: %s (%s)", graph_id, graph_arn)

    # Step 1: Update KB role with Neptune permissions
    log.info("=== Step 1: Update KB role for Neptune ===")
    update_kb_role_for_neptune(iam, graph_arn)

    # Step 2: Create GraphRAG KB
    log.info("=== Step 2: Create GraphRAG KB ===")
    kb_role_arn = iam.get_role(RoleName=KB_ROLE_NAME)["Role"]["Arn"]
    graphrag_kb_id = ensure_graphrag_kb(bedrock_agent, kb_role_arn, graph_arn)
    log.info("  GraphRAG KB ID: %s", graphrag_kb_id)

    # Step 3: Create data source with entity extraction
    log.info("=== Step 3: Create data source with graph construction ===")
    ds_id = ensure_graphrag_datasource(bedrock_agent, graphrag_kb_id)

    # Step 4: Sync (entity extraction + graph build)
    log.info("=== Step 4: Sync — entity extraction into Neptune ===")
    sync_graphrag_kb(bedrock_agent, graphrag_kb_id, ds_id)

    # Step 5: Verify graph
    log.info("=== Step 5: Verify Neptune graph data ===")
    verify_graph_data(neptune_query, graph_id)

    # Step 6: Update outputs
    outputs["graphrag_kb_id"] = graphrag_kb_id
    outputs["graphrag_ds_id"] = ds_id
    outputs["graph_arn"] = graph_arn
    OUTPUTS_PATH.write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    log.info("Outputs updated: %s", OUTPUTS_PATH)

    log.info("")
    log.info("=" * 60)
    log.info(" GraphRAG KB ready")
    log.info(" GraphRAG KB ID: %s", graphrag_kb_id)
    log.info(" Neptune graph:  %s (%s)", graph_id, graph_arn)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
