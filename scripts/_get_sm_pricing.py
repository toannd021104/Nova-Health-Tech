"""Get SageMaker endpoint pricing for GPU instances in Singapore."""
import subprocess, json

instances = [
    "ml.g4dn.xlarge",
    "ml.g4dn.2xlarge",
    "ml.g5.xlarge",
    "ml.g5.2xlarge",
    "ml.g5.4xlarge",
]

print(f"{'Instance':<22} {'GPU':<20} {'VRAM':<8} {'$/hr':>8}  {'Tok/s est':>10}  {'Emergency TTFT est':>20}")
print("-"*95)

gpu_specs = {
    "ml.g4dn.xlarge":  ("1x T4",   "16GB",  30,  "~5-6s"),
    "ml.g4dn.2xlarge": ("1x T4",   "16GB",  30,  "~5-6s"),
    "ml.g5.xlarge":    ("1x A10G", "24GB",  60,  "~2.5-3s"),
    "ml.g5.2xlarge":   ("1x A10G", "24GB",  60,  "~2.5-3s"),
    "ml.g5.4xlarge":   ("1x A10G", "24GB",  60,  "~2.5-3s"),
}

for inst in instances:
    r = subprocess.run(
        ["aws","pricing","get-products","--service-code","AmazonSageMaker",
         "--region","us-east-1","--profile","gapv50k",
         "--filters",
         "Type=TERM_MATCH,Field=instanceName,Value=" + inst,
         "Type=TERM_MATCH,Field=location,Value=Asia Pacific (Singapore)",
         "Type=TERM_MATCH,Field=component,Value=Hosting",
         "--query","PriceList[0]","--output","text"],
        capture_output=True, text=True
    )
    try:
        d = json.loads(r.stdout)
        od = d["terms"]["OnDemand"]
        k = list(od.keys())[0]
        pd = od[k]["priceDimensions"]
        pk = list(pd.keys())[0]
        price = float(pd[pk]["pricePerUnit"]["USD"])
        gpu, vram, toks, ttft = gpu_specs.get(inst, ("?", "?", 0, "?"))
        print(f"{inst:<22} {gpu:<20} {vram:<8} {price:>8.4f}  {str(toks)+' tok/s':>10}  {ttft:>20}")
    except Exception as e:
        print(f"{inst:<22} ERROR: {e}")
