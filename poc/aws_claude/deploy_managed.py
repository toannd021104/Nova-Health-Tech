"""Deploy the full managed stack for Nova Health PoC (Version A).

Creates:
    1. S3 data source (reuses existing bucket, uploads only WHO B09540-eng.pdf)
    2. OpenSearch Serverless vector collection (for Bedrock KB)
    3. Neptune Analytics graph (for GraphRAG)
    4. Bedrock Knowledge Base (S3 + OpenSearch Serverless + Titan Embed v2)
    5. Bedrock Guardrails
    6. Bedrock Agent with tools

Profile: gapv50k
Region: ap-southeast-1
Data: ONLY data/who/B09540-eng.pdf (~198 pages, embed cost < $0.01)

Usage:
    python poc/aws_claude/deploy_managed.py
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

log = logging.getLogger("poc.deploy_managed")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

PROFILE = "gapv50k"
REGION = "ap-southeast-1"
EMBED_REGION = "ap-southeast-1"  # Cohere Embed v3 available in SG and supported by Bedrock KB
EMBED_MODEL_ID = "cohere.embed-multilingual-v3"  # Titan Embed v2 not in SG; Cohere v4 not supported by KB; use v3 multilingual
STACK_TAG = "poc-claude"
REPO = Path(__file__).resolve().parent.parent.parent

# Existing resources from deploy.py
BUCKET = "ha-cg9jlwnsyxvkzs1idwnrzxq-307711587176"
ACCOUNT = "307711587176"

# New resource names
COLLECTION_NAME = "nova-health-kb"
GRAPH_NAME = "nova-health-graph"
KB_NAME = "nova-health-who-kb"
KB_ROLE_NAME = "HA-YmVkcm9jay1rYi1yb2xl"  # ha(bedrock-kb-role)
GUARDRAIL_NAME = "nova-health-guardrail"
AGENT_NAME = "nova-health-agent"
AGENT_ROLE_NAME = "HA-YmVkcm9jay1hZ2VudC1yb2xl"  # ha(bedrock-agent-role)

# Data: only 1 WHO PDF
WHO_PDF = REPO / "data" / "who" / "B09540-eng.pdf"
S3_PREFIX = "kb-who/"


def wait_for(check_fn, desc: str, interval: int = 15, timeout: int = 600):
    """Poll check_fn until it returns a truthy value or timeout."""
    elapsed = 0
    while elapsed < timeout:
        result = check_fn()
        if result:
            return result
        log.info("  waiting for %s... (%ds)", desc, elapsed)
        time.sleep(interval)
        elapsed += interval
    raise TimeoutError(f"Timed out waiting for {desc}")


def main() -> int:
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    s3 = session.client("s3")
    iam = session.client("iam")
    aoss = session.client("opensearchserverless")
    neptune = session.client("neptune-graph")
    bedrock = session.client("bedrock")
    bedrock_agent = session.client("bedrock-agent")

    # Also need a Tokyo session for embed model verification
    # (KB creation handles cross-region embed internally)

    # ========== Step 1: Upload WHO PDF to S3 ==========
    log.info("=== Step 1: Upload WHO PDF to S3 ===")
    s3_key = f"{S3_PREFIX}B09540-eng.pdf"
    try:
        s3.head_object(Bucket=BUCKET, Key=s3_key)
        log.info("  already exists: s3://%s/%s", BUCKET, s3_key)
    except ClientError:
        if not WHO_PDF.exists():
            log.error("WHO PDF not found at %s", WHO_PDF)
            return 1
        log.info("  uploading %s to s3://%s/%s", WHO_PDF.name, BUCKET, s3_key)
        s3.upload_file(str(WHO_PDF), BUCKET, s3_key)
    log.info("  done. Data source: s3://%s/%s", BUCKET, S3_PREFIX)

    # ========== Step 2: IAM role for Bedrock KB ==========
    log.info("=== Step 2: IAM role for Bedrock KB ===")
    kb_role_arn = ensure_kb_role(iam)
    log.info("  KB role: %s", kb_role_arn)

    # ========== Step 3: OpenSearch Serverless collection ==========
    log.info("=== Step 3: OpenSearch Serverless vector collection ===")
    collection_id, collection_arn, collection_endpoint = ensure_aoss_collection(aoss)
    log.info("  collection: %s (%s)", COLLECTION_NAME, collection_id)
    log.info("  endpoint: %s", collection_endpoint)

    # ========== Step 4: Neptune Analytics graph ==========
    log.info("=== Step 4: Neptune Analytics graph ===")
    graph_id, graph_arn, graph_endpoint = ensure_neptune_graph(neptune)
    log.info("  graph: %s (%s)", GRAPH_NAME, graph_id)
    log.info("  endpoint: %s", graph_endpoint)

    # ========== Step 5: Bedrock Knowledge Base ==========
    log.info("=== Step 5: Bedrock Knowledge Base ===")
    kb_id = ensure_bedrock_kb(bedrock_agent, kb_role_arn, collection_arn, collection_endpoint)
    log.info("  KB ID: %s", kb_id)

    # ========== Step 6: Sync KB data source ==========
    log.info("=== Step 6: Sync KB data source ===")
    sync_kb(bedrock_agent, kb_id)

    # ========== Step 7: Bedrock Guardrails ==========
    log.info("=== Step 7: Bedrock Guardrails ===")
    guardrail_id = ensure_guardrails(bedrock)
    log.info("  Guardrail ID: %s", guardrail_id)

    # ========== Step 8: Bedrock Agent ==========
    log.info("=== Step 8: Bedrock Agent ===")
    agent_role_arn = ensure_agent_role(iam, kb_id)
    agent_id = ensure_bedrock_agent(bedrock_agent, agent_role_arn, kb_id, guardrail_id)
    log.info("  Agent ID: %s", agent_id)

    # ========== Summary ==========
    log.info("")
    log.info("=" * 60)
    log.info(" FULL MANAGED STACK DEPLOYED")
    log.info("=" * 60)
    log.info(" S3 data:              s3://%s/%s", BUCKET, S3_PREFIX)
    log.info(" OpenSearch Serverless: %s (%s)", COLLECTION_NAME, collection_id)
    log.info(" Neptune Analytics:     %s (%s)", GRAPH_NAME, graph_id)
    log.info(" Bedrock KB:           %s (%s)", KB_NAME, kb_id)
    log.info(" Bedrock Guardrail:    %s (%s)", GUARDRAIL_NAME, guardrail_id)
    log.info(" Bedrock Agent:        %s (%s)", AGENT_NAME, agent_id)
    log.info(" EC2 POC (existing):   47.130.120.152")
    log.info("=" * 60)

    # Save outputs
    outputs = {
        "bucket": BUCKET,
        "s3_prefix": S3_PREFIX,
        "collection_id": collection_id,
        "collection_endpoint": collection_endpoint,
        "graph_id": graph_id,
        "graph_endpoint": graph_endpoint,
        "kb_id": kb_id,
        "guardrail_id": guardrail_id,
        "agent_id": agent_id,
    }
    out_path = Path(__file__).parent / ".managed_outputs.json"
    out_path.write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    log.info(" Outputs saved to %s", out_path)

    return 0


# ==================== IAM Roles ====================

def ensure_kb_role(iam) -> str:
    """Create IAM role for Bedrock KB to access S3 and OpenSearch Serverless."""
    try:
        role = iam.get_role(RoleName=KB_ROLE_NAME)
        return role["Role"]["Arn"]
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchEntity":
            raise

    log.info("  creating IAM role %s", KB_ROLE_NAME)
    trust = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock.amazonaws.com"},
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {"aws:SourceAccount": ACCOUNT},
            }
        }]
    }
    iam.create_role(
        RoleName=KB_ROLE_NAME,
        AssumeRolePolicyDocument=json.dumps(trust),
        Tags=[{"Key": "Stack", "Value": STACK_TAG}],
    )

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [f"arn:aws:s3:::{BUCKET}", f"arn:aws:s3:::{BUCKET}/*"],
            },
            {
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel"],
                "Resource": [
                    f"arn:aws:bedrock:{REGION}::foundation-model/{EMBED_MODEL_ID}",
                ],
            },
            {
                "Effect": "Allow",
                "Action": ["aoss:APIAccessAll"],
                "Resource": [f"arn:aws:aoss:{REGION}:{ACCOUNT}:collection/*"],
            },
        ]
    }
    iam.put_role_policy(
        RoleName=KB_ROLE_NAME,
        PolicyName="bedrock-kb-access",
        PolicyDocument=json.dumps(policy),
    )
    time.sleep(10)  # IAM propagation
    return iam.get_role(RoleName=KB_ROLE_NAME)["Role"]["Arn"]


def ensure_agent_role(iam, kb_id: str) -> str:
    """Create IAM role for Bedrock Agent."""
    try:
        role = iam.get_role(RoleName=AGENT_ROLE_NAME)
        return role["Role"]["Arn"]
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchEntity":
            raise

    log.info("  creating IAM role %s", AGENT_ROLE_NAME)
    trust = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock.amazonaws.com"},
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {"aws:SourceAccount": ACCOUNT},
            }
        }]
    }
    iam.create_role(
        RoleName=AGENT_ROLE_NAME,
        AssumeRolePolicyDocument=json.dumps(trust),
        Tags=[{"Key": "Stack", "Value": STACK_TAG}],
    )

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:Retrieve",
                    "bedrock:RetrieveAndGenerate",
                ],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "Action": ["bedrock:Retrieve"],
                "Resource": [f"arn:aws:bedrock:{REGION}:{ACCOUNT}:knowledge-base/{kb_id}"],
            },
        ]
    }
    iam.put_role_policy(
        RoleName=AGENT_ROLE_NAME,
        PolicyName="bedrock-agent-access",
        PolicyDocument=json.dumps(policy),
    )
    time.sleep(10)
    return iam.get_role(RoleName=AGENT_ROLE_NAME)["Role"]["Arn"]


# ==================== OpenSearch Serverless ====================

def ensure_aoss_collection(aoss) -> tuple[str, str, str]:
    """Create OpenSearch Serverless vector collection."""
    # Check if exists
    resp = aoss.list_collections(
        collectionFilters={"name": COLLECTION_NAME}
    )
    summaries = resp.get("collectionSummaries", [])
    if summaries:
        c = summaries[0]
        cid = c["id"]
        # Get endpoint
        detail = aoss.batch_get_collection(ids=[cid])["collectionDetails"][0]
        endpoint = detail.get("collectionEndpoint", "")
        arn = detail.get("arn", "")
        if detail["status"] != "ACTIVE":
            log.info("  collection exists but status=%s, waiting...", detail["status"])
            endpoint = wait_for_collection_active(aoss, cid)
            detail = aoss.batch_get_collection(ids=[cid])["collectionDetails"][0]
            arn = detail["arn"]
        return cid, arn, endpoint

    # Create encryption policy
    log.info("  creating encryption policy")
    enc_policy = json.dumps({
        "Rules": [{"ResourceType": "collection", "Resource": [f"collection/{COLLECTION_NAME}"]}],
        "AWSOwnedKey": True,
    })
    try:
        aoss.create_security_policy(
            name=f"{COLLECTION_NAME}-enc",
            type="encryption",
            policy=enc_policy,
        )
    except ClientError as e:
        if "ConflictException" not in str(e):
            raise

    # Create network policy (public access for demo)
    log.info("  creating network policy")
    net_policy = json.dumps([{
        "Rules": [
            {"ResourceType": "collection", "Resource": [f"collection/{COLLECTION_NAME}"]},
            {"ResourceType": "dashboard", "Resource": [f"collection/{COLLECTION_NAME}"]},
        ],
        "AllowFromPublic": True,
    }])
    try:
        aoss.create_security_policy(
            name=f"{COLLECTION_NAME}-net",
            type="network",
            policy=net_policy,
        )
    except ClientError as e:
        if "ConflictException" not in str(e):
            raise

    # Create data access policy
    log.info("  creating data access policy")
    access_policy = json.dumps([{
        "Rules": [
            {
                "ResourceType": "collection",
                "Resource": [f"collection/{COLLECTION_NAME}"],
                "Permission": ["aoss:CreateCollectionItems", "aoss:UpdateCollectionItems",
                               "aoss:DescribeCollectionItems"],
            },
            {
                "ResourceType": "index",
                "Resource": [f"index/{COLLECTION_NAME}/*"],
                "Permission": ["aoss:CreateIndex", "aoss:UpdateIndex", "aoss:DescribeIndex",
                               "aoss:ReadDocument", "aoss:WriteDocument"],
            },
        ],
        "Principal": [
            f"arn:aws:iam::{ACCOUNT}:user/hai.anh",
            f"arn:aws:iam::{ACCOUNT}:role/{KB_ROLE_NAME}",
            f"arn:aws:iam::{ACCOUNT}:role/{AGENT_ROLE_NAME}",
        ],
    }])
    try:
        aoss.create_access_policy(
            name=f"{COLLECTION_NAME}-access",
            type="data",
            policy=access_policy,
        )
    except ClientError as e:
        if "ConflictException" not in str(e):
            raise

    # Create collection
    log.info("  creating collection %s (type=VECTORSEARCH)", COLLECTION_NAME)
    resp = aoss.create_collection(
        name=COLLECTION_NAME,
        type="VECTORSEARCH",
        tags=[{"key": "Stack", "value": STACK_TAG}],
    )
    cid = resp["createCollectionDetail"]["id"]

    # Wait for ACTIVE
    endpoint = wait_for_collection_active(aoss, cid)
    detail = aoss.batch_get_collection(ids=[cid])["collectionDetails"][0]
    arn = detail["arn"]
    return cid, arn, endpoint


def wait_for_collection_active(aoss, cid: str) -> str:
    def check():
        detail = aoss.batch_get_collection(ids=[cid])["collectionDetails"][0]
        if detail["status"] == "ACTIVE":
            return detail.get("collectionEndpoint", "")
        return None
    return wait_for(check, f"collection {cid} ACTIVE", interval=20, timeout=600)


# ==================== Neptune Analytics ====================

def ensure_neptune_graph(neptune) -> tuple[str, str, str]:
    """Create Neptune Analytics graph."""
    # Check existing
    graphs = neptune.list_graphs()["graphs"]
    for g in graphs:
        if g["name"] == GRAPH_NAME:
            gid = g["id"]
            arn = g["arn"]
            detail = neptune.get_graph(graphIdentifier=gid)
            endpoint = detail.get("endpoint", "")
            if detail["status"] != "AVAILABLE":
                log.info("  graph exists but status=%s, waiting...", detail["status"])
                wait_for(
                    lambda: neptune.get_graph(graphIdentifier=gid)["status"] == "AVAILABLE",
                    f"graph {gid} AVAILABLE", interval=20, timeout=600
                )
                endpoint = neptune.get_graph(graphIdentifier=gid).get("endpoint", "")
            return gid, arn, endpoint

    log.info("  creating Neptune Analytics graph %s (1 m-NCU)", GRAPH_NAME)
    resp = neptune.create_graph(
        graphName=GRAPH_NAME,
        provisionedMemory=32,  # minimum: 32 m-NCU (smallest available)
        publicConnectivity=True,
        replicaCount=0,
        tags={"Stack": STACK_TAG},
    )
    gid = resp["id"]
    arn = resp["arn"]

    # Wait for AVAILABLE
    def check():
        detail = neptune.get_graph(graphIdentifier=gid)
        if detail["status"] == "AVAILABLE":
            return detail.get("endpoint", "")
        return None
    endpoint = wait_for(check, f"graph {gid} AVAILABLE", interval=20, timeout=900)
    return gid, arn, endpoint


# ==================== OpenSearch Serverless Index ====================

def create_aoss_index(collection_endpoint: str, index_name: str):
    """Create the vector index in OpenSearch Serverless using the REST API."""
    from opensearchpy import OpenSearch, RequestsHttpConnection
    from requests_aws4auth import AWS4Auth

    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    credentials = session.get_credentials().get_frozen_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        REGION,
        "aoss",
        session_token=credentials.token,
    )

    # Strip https:// for the host
    host = collection_endpoint.replace("https://", "")

    client = OpenSearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30,
    )

    # Check if index exists
    if client.indices.exists(index=index_name):
        log.info("  index '%s' already exists", index_name)
        return

    log.info("  creating index '%s' in OpenSearch Serverless", index_name)
    # Cohere Embed Multilingual v3 produces 1024-dim vectors
    index_body = {
        "settings": {
            "index": {
                "knn": True,
            }
        },
        "mappings": {
            "properties": {
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 1024,
                    "method": {
                        "engine": "faiss",
                        "name": "hnsw",
                        "parameters": {
                            "ef_construction": 256,
                            "m": 48,
                        },
                    },
                },
                "text": {"type": "text"},
                "metadata": {"type": "text"},
                "bedrock-knowledge-base-default-vector": {
                    "type": "knn_vector",
                    "dimension": 1024,
                    "method": {
                        "engine": "faiss",
                        "name": "hnsw",
                        "parameters": {
                            "ef_construction": 256,
                            "m": 48,
                        },
                    },
                },
                "AMAZON_BEDROCK_TEXT_CHUNK": {"type": "text"},
                "AMAZON_BEDROCK_METADATA": {"type": "text"},
            }
        }
    }
    client.indices.create(index=index_name, body=index_body)
    log.info("  index '%s' created successfully", index_name)


# ==================== Bedrock Knowledge Base ====================

def ensure_bedrock_kb(bedrock_agent, kb_role_arn: str, collection_arn: str, collection_endpoint: str) -> str:
    """Create Bedrock Knowledge Base with OpenSearch Serverless."""
    # Check existing
    kbs = bedrock_agent.list_knowledge_bases()["knowledgeBaseSummaries"]
    for kb in kbs:
        if kb["name"] == KB_NAME:
            return kb["knowledgeBaseId"]

    # The index name in OpenSearch Serverless
    index_name = "bedrock-kb-who"

    # Must create the index in OpenSearch Serverless BEFORE creating the KB
    create_aoss_index(collection_endpoint, index_name)
    # Wait for index to propagate
    log.info("  waiting 30s for index propagation...")
    time.sleep(30)

    log.info("  creating Bedrock KB %s", KB_NAME)

    resp = bedrock_agent.create_knowledge_base(
        name=KB_NAME,
        description="Nova Health WHO guidelines KB (B09540-eng.pdf only)",
        roleArn=kb_role_arn,
        knowledgeBaseConfiguration={
            "type": "VECTOR",
            "vectorKnowledgeBaseConfiguration": {
                "embeddingModelArn": f"arn:aws:bedrock:{REGION}::foundation-model/{EMBED_MODEL_ID}",
            },
        },
        storageConfiguration={
            "type": "OPENSEARCH_SERVERLESS",
            "opensearchServerlessConfiguration": {
                "collectionArn": collection_arn,
                "vectorIndexName": index_name,
                "fieldMapping": {
                    "vectorField": "bedrock-knowledge-base-default-vector",
                    "textField": "AMAZON_BEDROCK_TEXT_CHUNK",
                    "metadataField": "AMAZON_BEDROCK_METADATA",
                },
            },
        },
        tags={"Stack": STACK_TAG},
    )
    kb_id = resp["knowledgeBase"]["knowledgeBaseId"]

    # Wait for ACTIVE
    def check():
        kb = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)["knowledgeBase"]
        return kb_id if kb["status"] == "ACTIVE" else None
    wait_for(check, f"KB {kb_id} ACTIVE", interval=10, timeout=300)

    # Create S3 data source
    log.info("  creating S3 data source for KB")
    bedrock_agent.create_data_source(
        knowledgeBaseId=kb_id,
        name="who-guidelines",
        description="WHO B09540-eng.pdf",
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": {
                "bucketArn": f"arn:aws:s3:::{BUCKET}",
                "inclusionPrefixes": [S3_PREFIX],
            },
        },
    )

    return kb_id


def sync_kb(bedrock_agent, kb_id: str):
    """Start ingestion job to sync S3 data into the KB."""
    # Get data source ID
    ds_list = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)["dataSourceSummaries"]
    if not ds_list:
        log.warning("  no data sources found for KB %s", kb_id)
        return
    ds_id = ds_list[0]["dataSourceId"]

    log.info("  starting ingestion job for KB %s, data source %s", kb_id, ds_id)
    resp = bedrock_agent.start_ingestion_job(
        knowledgeBaseId=kb_id,
        dataSourceId=ds_id,
    )
    job_id = resp["ingestionJob"]["ingestionJobId"]
    log.info("  ingestion job started: %s", job_id)

    # Wait for completion
    def check():
        job = bedrock_agent.get_ingestion_job(
            knowledgeBaseId=kb_id, dataSourceId=ds_id, ingestionJobId=job_id
        )["ingestionJob"]
        status = job["status"]
        if status in ("COMPLETE", "FAILED", "PARTIALLY_FAILED"):
            log.info("  ingestion job %s: %s", job_id, status)
            if "statistics" in job:
                stats = job["statistics"]
                log.info("    scanned=%s, indexed=%s, failed=%s",
                         stats.get("numberOfDocumentsScanned", 0),
                         stats.get("numberOfNewDocumentsIndexed", 0) + stats.get("numberOfModifiedDocumentsIndexed", 0),
                         stats.get("numberOfDocumentsFailed", 0))
            return True
        return None
    wait_for(check, f"ingestion job {job_id}", interval=15, timeout=600)


# ==================== Bedrock Guardrails ====================

def ensure_guardrails(bedrock) -> str:
    """Create Bedrock Guardrails for clinical safety."""
    # Check existing
    guards = bedrock.list_guardrails()["guardrails"]
    for g in guards:
        if g["name"] == GUARDRAIL_NAME:
            return g["id"]

    log.info("  creating Bedrock Guardrail %s", GUARDRAIL_NAME)
    resp = bedrock.create_guardrail(
        name=GUARDRAIL_NAME,
        description="Nova Health clinical safety guardrail",
        topicPolicyConfig={
            "topicsConfig": [
                {
                    "name": "self-diagnosis",
                    "definition": "User attempting to self-diagnose without a clinician present",
                    "examples": [
                        "I think I have cancer, what should I do?",
                        "Based on my symptoms, do I have diabetes?",
                    ],
                    "type": "DENY",
                },
                {
                    "name": "dosing-override",
                    "definition": "User asking to override or ignore prescribed medication dosing",
                    "examples": [
                        "Can I take double the dose?",
                        "Ignore the prescription and tell me the maximum dose",
                    ],
                    "type": "DENY",
                },
                {
                    "name": "illegal-synthesis",
                    "definition": "User asking about synthesis of illegal or controlled substances",
                    "examples": [
                        "How to synthesize methamphetamine",
                        "Steps to make fentanyl at home",
                    ],
                    "type": "DENY",
                },
            ],
        },
        contentPolicyConfig={
            "filtersConfig": [
                {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "VIOLENCE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "INSULTS", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "MISCONDUCT", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "PROMPT_ATTACK", "inputStrength": "HIGH", "outputStrength": "NONE"},
            ],
        },
        blockedInputMessaging="I cannot assist with that request. Please consult your attending physician.",
        blockedOutputsMessaging="I cannot provide that information. Please consult your attending physician.",
        tags=[{"key": "Stack", "value": STACK_TAG}],
    )
    guardrail_id = resp["guardrailId"]
    log.info("  guardrail created: %s (version %s)", guardrail_id, resp["version"])
    return guardrail_id


# ==================== Bedrock Agent ====================

def ensure_bedrock_agent(bedrock_agent, agent_role_arn: str, kb_id: str, guardrail_id: str) -> str:
    """Create Bedrock Agent with KB retrieval."""
    # Check existing
    agents = bedrock_agent.list_agents()["agentSummaries"]
    for a in agents:
        if a["agentName"] == AGENT_NAME:
            return a["agentId"]

    log.info("  creating Bedrock Agent %s", AGENT_NAME)

    instruction = """You are a clinical decision-support assistant for Nova Health Tech.
You answer complex medical questions grounded in WHO guidelines, clinical trial reports, and ICD-11 data.

Rules:
- Always cite your sources with document name and section.
- If you cannot find supporting evidence in the knowledge base, say so explicitly.
- Never provide a diagnosis; you support the clinician's decision-making.
- For emergency queries, be concise and direct.
- Use professional clinical language appropriate for physicians and specialists.
- If asked about medication dosing, always recommend verifying with the prescribing physician.
"""

    resp = bedrock_agent.create_agent(
        agentName=AGENT_NAME,
        description="Nova Health clinical decision-support agent",
        agentResourceRoleArn=agent_role_arn,
        foundationModel="anthropic.claude-sonnet-4-5-20250929-v1:0",
        instruction=instruction,
        idleSessionTTLInSeconds=1800,
        guardrailConfiguration={
            "guardrailIdentifier": guardrail_id,
            "guardrailVersion": "DRAFT",
        },
        tags={"Stack": STACK_TAG},
    )
    agent_id = resp["agent"]["agentId"]

    # Wait for agent to be ready
    time.sleep(5)

    # Associate KB
    log.info("  associating KB %s with agent %s", kb_id, agent_id)
    bedrock_agent.associate_agent_knowledge_base(
        agentId=agent_id,
        agentVersion="DRAFT",
        knowledgeBaseId=kb_id,
        description="WHO clinical guidelines knowledge base",
        knowledgeBaseState="ENABLED",
    )

    # Prepare agent
    log.info("  preparing agent %s", agent_id)
    bedrock_agent.prepare_agent(agentId=agent_id)

    # Wait for prepared
    def check():
        a = bedrock_agent.get_agent(agentId=agent_id)["agent"]
        return agent_id if a["agentStatus"] == "PREPARED" else None
    wait_for(check, f"agent {agent_id} PREPARED", interval=10, timeout=300)

    return agent_id


if __name__ == "__main__":
    sys.exit(main())
