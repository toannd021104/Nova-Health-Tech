"""Calculate actual Version B PoC costs from resource usage."""
import boto3
from datetime import datetime, timezone

session = boto3.Session(profile_name="gapv50k", region_name="ap-southeast-1")
sm = session.client("sagemaker")

print("=" * 70)
print("VERSION B PoC — Actual Resource Usage & Estimated Cost")
print("=" * 70)

# ── Training jobs ─────────────────────────────────────────────────────────────
print("\n--- SageMaker Training Jobs ---")
jobs = sm.list_training_jobs(
    NameContains="HA-c20tdHJhaW5pbmctcGhhc2Ux",
    MaxResults=20,
)["TrainingJobSummaries"]

training_cost = 0.0
for j in jobs:
    name = j["TrainingJobName"]
    status = j["TrainingJobStatus"]
    desc = sm.describe_training_job(TrainingJobName=name)
    elapsed_s = desc.get("TrainingTimeInSeconds", 0)
    instance = desc["ResourceConfig"]["InstanceType"]
    # Pricing: ml.g4dn.2xlarge = $1.315/hr in ap-southeast-1
    price_map = {
        "ml.g4dn.2xlarge": 1.315,
        "ml.g4dn.xlarge":  1.0304,
        "ml.g5.xlarge":    1.9712,
    }
    rate = price_map.get(instance, 1.0)
    cost = (elapsed_s / 3600) * rate
    training_cost += cost
    print(f"  {name[-30:]:<30} {status:<12} {instance:<20} "
          f"{elapsed_s/3600:.2f}hr × ${rate:.3f}/hr = ${cost:.4f}")

print(f"\n  Training total: ${training_cost:.4f}")

# ── Endpoints ─────────────────────────────────────────────────────────────────
print("\n--- SageMaker Endpoints ---")
endpoints = sm.list_endpoints()["Endpoints"]
endpoint_cost = 0.0
for ep in endpoints:
    name = ep["EndpointName"]
    status = ep["EndpointStatus"]
    desc = sm.describe_endpoint(EndpointName=name)
    created = desc["CreationTime"]
    now = datetime.now(timezone.utc)
    hours_running = (now - created).total_seconds() / 3600
    # Get instance type from endpoint config
    epc = sm.describe_endpoint_config(
        EndpointConfigName=desc["EndpointConfigName"]
    )
    instance = epc["ProductionVariants"][0].get("InstanceType", "unknown")
    price_map = {
        "ml.g4dn.xlarge":  1.0304,
        "ml.g5.xlarge":    1.9712,
        "ml.g4dn.2xlarge": 1.315,
    }
    rate = price_map.get(instance, 1.0)
    cost = hours_running * rate
    endpoint_cost += cost
    print(f"  {name:<40} {status:<12} {instance:<20} "
          f"{hours_running:.1f}hr × ${rate:.3f}/hr = ${cost:.4f}")

print(f"\n  Endpoint total so far: ${endpoint_cost:.4f}")

# ── EC2 ───────────────────────────────────────────────────────────────────────
print("\n--- EC2 Instances ---")
ec2 = session.client("ec2")
instances = ec2.describe_instances(
    Filters=[{"Name": "tag:Owner", "Values": ["nova-health-poc"]}]
)
ec2_cost = 0.0
for r in instances["Reservations"]:
    for i in r["Instances"]:
        if i["State"]["Name"] not in ("running", "stopped"):
            continue
        itype = i["InstanceType"]
        launch = i["LaunchTime"]
        now = datetime.now(timezone.utc)
        hours = (now - launch).total_seconds() / 3600
        # t4g.small = $0.023/hr
        rate = 0.023
        cost = hours * rate
        ec2_cost += cost
        name = next((t["Value"] for t in i.get("Tags", []) if t["Key"] == "Name"), "unnamed")
        print(f"  {name:<30} {itype:<15} {i['State']['Name']:<10} "
              f"{hours:.1f}hr × ${rate:.3f}/hr = ${cost:.4f}")

print(f"\n  EC2 total so far: ${ec2_cost:.4f}")

# ── Bedrock KB ────────────────────────────────────────────────────────────────
print("\n--- Bedrock Knowledge Bases (always-on) ---")
# OpenSearch Serverless: 2 OCU × $0.24/hr
# Neptune Analytics: 1 m-NCU × $0.16/hr
# Estimate from KB creation date
bedrock_agent = session.client("bedrock-agent")
kbs = bedrock_agent.list_knowledge_bases()["knowledgeBaseSummaries"]
kb_cost = 0.0
for kb in kbs:
    kb_id = kb["knowledgeBaseId"]
    desc = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)["knowledgeBase"]
    created = desc["createdAt"]
    now = datetime.now(timezone.utc)
    hours = (now - created).total_seconds() / 3600
    # Rough: vector KB = 2 OCU × $0.24 = $0.48/hr, graph KB = 1 m-NCU × $0.16 = $0.16/hr
    rate = 0.48 if "graphrag" not in kb["name"].lower() else 0.16
    cost = hours * rate
    kb_cost += cost
    print(f"  {kb['name']:<35} {kb_id}  {hours:.0f}hr × ${rate:.2f}/hr = ${cost:.2f}")

print(f"\n  KB total so far: ${kb_cost:.2f}")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("ACTUAL COST SUMMARY — Version B PoC (May 2026)")
print("=" * 70)
grand = training_cost + endpoint_cost + ec2_cost + kb_cost
print(f"  SageMaker Training Jobs:  ${training_cost:>8.2f}")
print(f"  SageMaker Endpoint:       ${endpoint_cost:>8.2f}")
print(f"  EC2 (web server):         ${ec2_cost:>8.2f}")
print(f"  Bedrock KBs (est.):       ${kb_cost:>8.2f}")
print(f"  {'─'*35}")
print(f"  TOTAL (PoC to date):      ${grand:>8.2f}")
print()
print("Note: Bedrock inference (Claude/Nova) billed separately via 'Claude Platform'")
print("      Cost Explorer shows $7.11 for Claude Platform (May 1-18)")
