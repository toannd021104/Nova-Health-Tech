"""Test SageMaker Notebook Jupyter API interaction via presigned URL."""
import subprocess, json, urllib.request, urllib.parse

# Get a fresh presigned URL
r = subprocess.run(
    ["aws","sagemaker","create-presigned-notebook-instance-url",
     "--notebook-instance-name","nova-qwen-finetune-test",
     "--region","ap-southeast-1","--profile","gapv50k","--output","json"],
    capture_output=True, text=True
)
data = json.loads(r.stdout)
presigned_url = data["AuthorizedUrl"]
print(f"Presigned URL obtained: {presigned_url[:80]}...")

# Extract the auth token from the URL
parsed = urllib.parse.urlparse(presigned_url)
params = urllib.parse.parse_qs(parsed.query)
auth_token = params.get("authToken", [""])[0]
base_url = f"{parsed.scheme}://{parsed.netloc}"
print(f"Base URL: {base_url}")
print(f"Auth token length: {len(auth_token)}")

# Try to hit the Jupyter API with the token
api_url = f"{base_url}/api/kernelspecs"
req = urllib.request.Request(
    api_url,
    headers={"Authorization": f"token {auth_token}"}
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read())
        print(f"\nKernel specs available: {list(body.get('kernelspecs', {}).keys())}")
except Exception as e:
    print(f"\nDirect API call failed: {e}")
    print("(Expected — SageMaker Notebook uses cookie-based auth, not token header)")

# Try the /api/contents endpoint
api_url2 = f"{base_url}/api/contents"
req2 = urllib.request.Request(
    api_url2,
    headers={"Authorization": f"token {auth_token}"}
)
try:
    with urllib.request.urlopen(req2, timeout=10) as resp:
        body = json.loads(resp.read())
        print(f"Contents API works: {body}")
except Exception as e:
    print(f"Contents API failed: {e}")
