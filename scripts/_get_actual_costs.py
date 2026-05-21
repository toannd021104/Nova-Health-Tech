"""Get actual AWS costs for May 2026 — Version B PoC."""
import boto3, json

session = boto3.Session(profile_name="gapv50k", region_name="us-east-1")
ce = session.client("ce")

# Total cost by service
resp = ce.get_cost_and_usage(
    TimePeriod={"Start": "2026-05-01", "End": "2026-05-19"},
    Granularity="MONTHLY",
    Metrics=["UnblendedCost"],
    GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
)

rows = resp["ResultsByTime"][0]["Groups"]
rows.sort(key=lambda x: -float(x["Metrics"]["UnblendedCost"]["Amount"]))

total = sum(float(r["Metrics"]["UnblendedCost"]["Amount"]) for r in rows)
print(f"{'Service':<50} {'Cost (USD)':>12}")
print("-" * 65)
for r in rows:
    amt = float(r["Metrics"]["UnblendedCost"]["Amount"])
    if amt > 0.001:
        print(f"{r['Keys'][0]:<50} ${amt:>11.4f}")
print("-" * 65)
print(f"{'TOTAL (May 1-18, 2026)':<50} ${total:>11.4f}")

# Also get SageMaker breakdown by usage type
print("\n\n=== SageMaker detail by usage type ===")
resp2 = ce.get_cost_and_usage(
    TimePeriod={"Start": "2026-05-01", "End": "2026-05-19"},
    Granularity="MONTHLY",
    Metrics=["UnblendedCost", "UsageQuantity"],
    Filter={"Dimensions": {"Key": "SERVICE", "Values": ["Amazon SageMaker"]}},
    GroupBy=[{"Type": "DIMENSION", "Key": "USAGE_TYPE"}],
)
rows2 = resp2["ResultsByTime"][0]["Groups"]
rows2.sort(key=lambda x: -float(x["Metrics"]["UnblendedCost"]["Amount"]))
for r in rows2:
    amt = float(r["Metrics"]["UnblendedCost"]["Amount"])
    qty = float(r["Metrics"]["UsageQuantity"]["Amount"])
    if amt > 0.001:
        print(f"  {r['Keys'][0]:<55} ${amt:>8.4f}  qty={qty:.2f}")

# Bedrock breakdown
print("\n\n=== Bedrock detail by usage type ===")
resp3 = ce.get_cost_and_usage(
    TimePeriod={"Start": "2026-05-01", "End": "2026-05-19"},
    Granularity="MONTHLY",
    Metrics=["UnblendedCost", "UsageQuantity"],
    Filter={"Dimensions": {"Key": "SERVICE", "Values": ["Amazon Bedrock"]}},
    GroupBy=[{"Type": "DIMENSION", "Key": "USAGE_TYPE"}],
)
rows3 = resp3["ResultsByTime"][0]["Groups"]
rows3.sort(key=lambda x: -float(x["Metrics"]["UnblendedCost"]["Amount"]))
for r in rows3:
    amt = float(r["Metrics"]["UnblendedCost"]["Amount"])
    qty = float(r["Metrics"]["UsageQuantity"]["Amount"])
    if amt > 0.001:
        print(f"  {r['Keys'][0]:<55} ${amt:>8.4f}  qty={qty:.2f}")
