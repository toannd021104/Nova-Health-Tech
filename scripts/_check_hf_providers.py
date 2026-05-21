import urllib.request, json

for model_id in ["Qwen/Qwen3.5-397B-A17B", "Qwen/Qwen3.5-122B-A10B"]:
    url = f"https://huggingface.co/api/models/{model_id}?expand[]=inferenceProviderMapping"
    r = urllib.request.urlopen(url)
    data = json.loads(r.read())
    providers = data.get("inferenceProviderMapping", {})
    print(f"\n{model_id}:")
    for p, v in providers.items():
        print(f"  {p:20s} status={v['status']}  id={v['providerId']}")
