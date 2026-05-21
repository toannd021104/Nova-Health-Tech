import subprocess, json

r = subprocess.run(
    ["aws","service-quotas","list-service-quotas","--service-code","sagemaker",
     "--region","ap-southeast-1","--profile","gapv50k","--output","json"],
    capture_output=True, text=True
)
data = json.loads(r.stdout)
training = [
    q for q in data["Quotas"]
    if "training" in q["QuotaName"].lower()
    and any(k in q["QuotaName"] for k in ["g4dn","g5","g6","p3","p4"])
]
print(f"{'Value':>5}  {'QuotaCode':<40}  QuotaName")
print("-"*100)
for q in sorted(training, key=lambda x: x["QuotaName"]):
    print(f"{int(q['Value']):>5}  {q['QuotaCode']:<40}  {q['QuotaName']}")
