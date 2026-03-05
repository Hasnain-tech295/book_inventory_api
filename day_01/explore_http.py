# Goal: See exactly what HTTP requests and responses look like

import requests  # pip install requests

# --- Make a GET request to a real public API ---
response = requests.get("https://httpbin.org/get?name=ada&role=engineer")

# --- Inspect the request that was sent ---
print("=== REQUEST ===")
print(f"Method:  {response.request.method}")
print(f"URL:     {response.request.url}")
print(f"Headers: {dict(response.request.headers)}")

# --- Inspect the response ---
print("\n=== RESPONSE ===")
print(f"Status Code: {response.status_code}")
print(f"Headers:     {dict(response.headers)}")
print(f"Body (JSON): {response.json()}")

# --- Status code meaning ---
if response.status_code == 200:
    print("\n✅ Request succeeded")
elif response.status_code >= 400:
    print("\n❌ Request failed")