"""Re-ingest Bedrock KB with multi-strategy chunking.

Strategy:
  - WHO guidelines (B09540-eng.pdf): Hierarchical chunking
    Parent: 1500 tokens, Child: 300 tokens, Overlap: 0
  - Clinical trial PDFs: Semantic chunking
    Max tokens: 800, Buffer: 1, Breakpoint: 80th percentile

Steps:
  1. Delete existing data source (default chunking)
  2. Create new data source for WHO with hierarchical chunking
  3. Create new data source for clinical trials with semantic chunking
  4. Sync both

Profile: gapv50k | Region: ap-southeast-1
"""
import json
import logging
import time
from pathlib import Path

import boto3

log = logging.getLogger("reingest")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

PROFILE = "gapv50k"
REGION = "ap-southeast-1"
KB_ID = "MUEEBGPRSJ"
BUCKET = "ha-cg9jlwnsyxvkzs1idwnrzxq-307711587176"


def wait_ingestion(bedrock_agent, kb_id, ds_id, job_id, timeout=600):
    elapsed = 0
    while elapsed < timeout:
        job = bedrock_agent.get_ingestion_job(
            knowledgeBaseId=kb_id, dataSourceId=ds_id, ingestionJobId=job_id
        )["ingestionJob"]
        status = job["status"]
        if status in ("COMPLETE", "FAILED", "PARTIALLY_FAILED"):
            stats = job.get("statistics", {})
            log.info("  %s: scanned=%s indexed=%s failed=%s",
                     status,
                     stats.get("numberOfDocumentsScanned", 0),
                     stats.get("numberOfNewDocumentsIndexed", 0) + stats.get("numberOfModifiedDocumentsIndexed", 0),
                     stats.get("numberOfDocumentsFailed", 0))
            if status == "FAILED":
                log.error("  reasons: %s", job.get("failureReasons", []))
            return status
        log.info("  waiting... (%ds) status=%s", elapsed, status)
        time.sleep(15)
        elapsed += 15
    raise TimeoutError("Ingestion timed out")


def main():
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    bedrock_agent = session.client("bedrock-agent")

    # List existing data sources
    ds_list = bedrock_agent.list_data_sources(knowledgeBaseId=KB_ID)["dataSourceSummaries"]
    log.info("Existing data sources: %d", len(ds_list))
    for ds in ds_list:
        log.info("  %s: %s", ds["dataSourceId"], ds["name"])

    # Delete existing data sources
    for ds in ds_list:
        log.info("Deleting data source %s (%s)", ds["dataSourceId"], ds["name"])
        bedrock_agent.delete_data_source(knowledgeBaseId=KB_ID, dataSourceId=ds["dataSourceId"])
        time.sleep(3)

    log.info("All old data sources deleted. Creating new ones with multi-strategy chunking.")

    # === Data Source 1: WHO guidelines with Hierarchical chunking ===
    log.info("\n=== Creating WHO data source (hierarchical chunking) ===")
    ds_who = bedrock_agent.create_data_source(
        knowledgeBaseId=KB_ID,
        name="who-guidelines-hierarchical",
        description="WHO B09540-eng.pdf with hierarchical chunking (parent 1500, child 300)",
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": {
                "bucketArn": f"arn:aws:s3:::{BUCKET}",
                "inclusionPrefixes": ["kb-who/"],
            },
        },
        vectorIngestionConfiguration={
            "chunkingConfiguration": {
                "chunkingStrategy": "HIERARCHICAL",
                "hierarchicalChunkingConfiguration": {
                    "levelConfigurations": [
                        {"maxTokens": 1500},  # parent
                        {"maxTokens": 300},   # child
                    ],
                    "overlapTokens": 30,
                },
            },
        },
    )
    ds_who_id = ds_who["dataSource"]["dataSourceId"]
    log.info("  WHO data source created: %s", ds_who_id)

    # === Data Source 2: Clinical trials with Semantic chunking ===
    log.info("\n=== Creating clinical trials data source (semantic chunking) ===")
    ds_trials = bedrock_agent.create_data_source(
        knowledgeBaseId=KB_ID,
        name="clinical-trials-semantic",
        description="12 department PMC papers with semantic chunking (max 800, buffer 1, breakpoint 80)",
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": {
                "bucketArn": f"arn:aws:s3:::{BUCKET}",
                "inclusionPrefixes": ["kb-src/departments/"],
            },
        },
        vectorIngestionConfiguration={
            "chunkingConfiguration": {
                "chunkingStrategy": "SEMANTIC",
                "semanticChunkingConfiguration": {
                    "maxTokens": 512,
                    "bufferSize": 1,
                    "breakpointPercentileThreshold": 80,
                },
            },
        },
    )
    ds_trials_id = ds_trials["dataSource"]["dataSourceId"]
    log.info("  Clinical trials data source created: %s", ds_trials_id)

    # === Data Source 3: ICD-11 with no chunking (each JSON = 1 chunk) ===
    log.info("\n=== Creating ICD-11 data source (no chunking) ===")
    ds_icd = bedrock_agent.create_data_source(
        knowledgeBaseId=KB_ID,
        name="icd11-no-chunking",
        description="ICD-11 JSON entities, each file = 1 chunk",
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": {
                "bucketArn": f"arn:aws:s3:::{BUCKET}",
                "inclusionPrefixes": ["kb-src/icd11/"],
            },
        },
        vectorIngestionConfiguration={
            "chunkingConfiguration": {
                "chunkingStrategy": "NONE",
            },
        },
    )
    ds_icd_id = ds_icd["dataSource"]["dataSourceId"]
    log.info("  ICD-11 data source created: %s", ds_icd_id)

    # === Sync all data sources ===
    log.info("\n=== Syncing all data sources ===")

    for ds_id, name in [(ds_who_id, "WHO"), (ds_trials_id, "Clinical trials"), (ds_icd_id, "ICD-11")]:
        log.info("\nSyncing %s (%s)...", name, ds_id)
        resp = bedrock_agent.start_ingestion_job(knowledgeBaseId=KB_ID, dataSourceId=ds_id)
        job_id = resp["ingestionJob"]["ingestionJobId"]
        log.info("  Job: %s", job_id)
        wait_ingestion(bedrock_agent, KB_ID, ds_id, job_id)

    log.info("\n" + "=" * 60)
    log.info(" Multi-strategy re-ingest complete!")
    log.info(" WHO:     hierarchical (parent 1500, child 300)")
    log.info(" Trials:  semantic (max 800, buffer 1, breakpoint 80)")
    log.info(" ICD-11:  no chunking (1 file = 1 chunk)")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
