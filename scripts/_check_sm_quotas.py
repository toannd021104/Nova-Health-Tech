import subprocess, json, sys

r = subprocess.run(
    ["aws","service-quotas","list-service-quotas","--service-code","sagemaker",
     "--region","ap-southeast-1","--profile","gapv50k","--output","json"],
    capture_output=True, text=True
)
data = json.loads(r.stdout)
gpu_quotas = [
    q for q in data["Quotas"]
    if q["Value"] > 0 and any(k in q["QuotaName"] for k in ["ml.g","ml.p"])
]
print(f"{'Value':>6}  {'Quota Name'}")
print("-"*80)
for q in sorted(gpu_quotas, key=lambda x: x["QuotaName"]):
    print(f"{q['Value']:>6.0f}  {q['QuotaName']}")
