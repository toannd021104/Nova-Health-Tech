import boto3, json

session = boto3.Session(profile_name="gapv50k", region_name="us-east-1")
ce = session.client("ce")

# Check all services May 10-13
resp = ce.get_cost_and_usage(
    TimePeriod={"Start": "2026-05-10", "End": "2026-05-13"},
    Granularity="DAILY",
    Metrics=["UnblendedCost", "UsageQuantity"],
    GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
)

print("=== All services with any cost, May 10-12 ===\n")
for day in resp["ResultsByTime"]:
    date = day["TimePeriod"]["Start"]
    groups = day["Groups"]
    services = []
    for g in groups:
        cost = float(g["Metrics"]["UnblendedCost"]["Amount"])
        qty = float(g["Metrics"]["UsageQuantity"]["Amount"])
        name = g["Keys"][0]
        services.append((name, cost, qty))
    services.sort(key=lambda x: -abs(x[1]))
    day_total = sum(c for _, c, _ in services)
    print(f"=== {date} (total: USD {day_total:.4f}) ===")
    for name, cost, qty in services:
        if abs(cost) > 0.0001 or "Bedrock" in name or "OpenSearch" in name or "Neptune" in name:
            print(f"  {name:<55} USD {cost:>9.4f}  qty={qty:.2f}")
    print()

# Also check Bedrock specifically with filter
print("\n=== Bedrock only (May 10-13) ===")
try:
    resp2 = ce.get_cost_and_usage(
        TimePeriod={"Start": "2026-05-10", "End": "2026-05-13"},
        Granularity="DAILY",
        Metrics=["UnblendedCost", "UsageQuantity"],
        Filter={"Dimensions": {"Key": "SERVICE", "Values": ["Amazon Bedrock"]}},
        GroupBy=[{"Type": "DIMENSION", "Key": "USAGE_TYPE"}],
    )
    for day in resp2["ResultsByTime"]:
        date = day["TimePeriod"]["Start"]
        groups = day["Groups"]
        day_total = sum(float(g["Metrics"]["UnblendedCost"]["Amount"]) for g in groups)
        print(f"\n{date} (Bedrock total: USD {day_total:.6f})")
        for g in groups:
            cost = float(g["Metrics"]["UnblendedCost"]["Amount"])
            qty = float(g["Metrics"]["UsageQuantity"]["Amount"])
            if abs(cost) > 0.000001 or qty > 0:
                print(f"  {g['Keys'][0]:<60} USD {cost:.6f}  qty={qty:.2f}")
except Exception as e:
    print(f"Error: {e}")

# Check OpenSearch and Neptune
print("\n=== OpenSearch Serverless (May 10-13) ===")
try:
    resp3 = ce.get_cost_and_usage(
        TimePeriod={"Start": "2026-05-10", "End": "2026-05-13"},
        Granularity="DAILY",
        Metrics=["UnblendedCost", "UsageQuantity"],
        Filter={"Dimensions": {"Key": "SERVICE", "Values": ["Amazon OpenSearch Service"]}},
        GroupBy=[{"Type": "DIMENSION", "Key": "USAGE_TYPE"}],
    )
    for day in resp3["ResultsByTime"]:
        date = day["TimePeriod"]["Start"]
        groups = day["Groups"]
        day_total = sum(float(g["Metrics"]["UnblendedCost"]["Amount"]) for g in groups)
        print(f"\n{date} (OpenSearch total: USD {day_total:.4f})")
        for g in groups:
            cost = float(g["Metrics"]["UnblendedCost"]["Amount"])
            qty = float(g["Metrics"]["UsageQuantity"]["Amount"])
            if abs(cost) > 0.001 or qty > 0:
                print(f"  {g['Keys'][0]:<60} USD {cost:.4f}  qty={qty:.2f}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Neptune Analytics (May 10-13) ===")
try:
    resp4 = ce.get_cost_and_usage(
        TimePeriod={"Start": "2026-05-10", "End": "2026-05-13"},
        Granularity="DAILY",
        Metrics=["UnblendedCost", "UsageQuantity"],
        Filter={"Dimensions": {"Key": "SERVICE", "Values": ["Amazon Neptune"]}},
        GroupBy=[{"Type": "DIMENSION", "Key": "USAGE_TYPE"}],
    )
    for day in resp4["ResultsByTime"]:
        date = day["TimePeriod"]["Start"]
        groups = day["Groups"]
        day_total = sum(float(g["Metrics"]["UnblendedCost"]["Amount"]) for g in groups)
        print(f"\n{date} (Neptune total: USD {day_total:.4f})")
        for g in groups:
            cost = float(g["Metrics"]["UnblendedCost"]["Amount"])
            qty = float(g["Metrics"]["UsageQuantity"]["Amount"])
            if abs(cost) > 0.001 or qty > 0:
                print(f"  {g['Keys'][0]:<60} USD {cost:.4f}  qty={qty:.2f}")
except Exception as e:
    print(f"Error: {e}")
