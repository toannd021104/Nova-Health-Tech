import boto3
session = boto3.Session(profile_name="gapv50k", region_name="ap-southeast-1")
ba = session.client("bedrock-agent")
KB_ID = "MUEEBGPRSJ"
ds_list = ba.list_data_sources(knowledgeBaseId=KB_ID)["dataSourceSummaries"]
for ds in ds_list:
    ds_id = ds["dataSourceId"]
    name = ds["name"]
    jobs = ba.list_ingestion_jobs(knowledgeBaseId=KB_ID, dataSourceId=ds_id, maxResults=1)
    latest = jobs["ingestionJobSummaries"][0] if jobs["ingestionJobSummaries"] else None
    status = latest["status"] if latest else "NO_JOBS"
    stats = ""
    if latest and latest.get("statistics"):
        s = latest["statistics"]
        scanned = s.get("numberOfDocumentsScanned", 0)
        indexed = s.get("numberOfNewDocumentsIndexed", 0) + s.get("numberOfModifiedDocumentsIndexed", 0)
        failed = s.get("numberOfDocumentsFailed", 0)
        stats = f" scanned={scanned} indexed={indexed} failed={failed}"
    print(f"{name}: {status}{stats}")
