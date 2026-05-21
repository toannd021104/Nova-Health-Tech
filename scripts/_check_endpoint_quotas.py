import subprocess, json

r = subprocess.run(
    ["aws","service-quotas","list-service-quotas","--service-code","sagemaker",
     "--region","ap-southeast-1","--profile","gapv50k","--output","json"],
    capture_output=True, text=True
)
data = json.loads(r.stdout)
gpu = [
    q for q in data["Quotas"]
    if q["Value"] > 0
    and any(k in q["QuotaName"] for k in ["g5","g6","g4dn","p3","p4"])
    and "endpoint" in q["QuotaName"].lower()
]
print(f"{'Value':>5}  {'Instance':<25}  QuotaName")
print("-"*80)
for q in sorted(gpu, key=lambda x: x["QuotaName"]):
    print(f"{int(q['Value']):>5}  {q['QuotaName']}")
