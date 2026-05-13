import requests, json, time

url = "http://47.130.120.152/api/chat/stream"
payload = {"message": "What dose of dexamethasone for severe COVID-19?", "emergency": True}

t0 = time.time()
resp = requests.post(url, json=payload, stream=True, timeout=30)
print(f"Status: {resp.status_code}")

t_first = None
token_count = 0
full_text = ""
for line in resp.iter_lines(decode_unicode=True):
    if not line:
        continue
    elapsed = time.time() - t0
    if line.startswith("event: "):
        etype = line[7:]
    elif line.startswith("data: "):
        data = json.loads(line[6:])
        if "text" in data:
            token_count += 1
            full_text += data["text"]
            if t_first is None:
                t_first = elapsed
                print(f"FIRST TOKEN at {t_first*1000:.0f}ms")
            if token_count <= 5:
                preview = data["text"][:50]
                print(f"  [{elapsed*1000:.0f}ms] token #{token_count}: {preview}")
        elif "error" in data:
            print(f"  ERROR: {data['error'][:200]}")
        elif "lane" in data:
            print(f"  ROUTE: {data}")

total = time.time() - t0
print(f"\nTTFT: {t_first*1000:.0f}ms" if t_first else "\nTTFT: no tokens received")
print(f"Total: {total*1000:.0f}ms")
print(f"Tokens: {token_count}")
print(f"Answer: {full_text[:300]}")
