import os, requests

BASE = "http://127.0.0.1:5000"
credentials = {"username": os.getenv("ADMIN_USERNAME"), "password": os.getenv("ADMIN_PASSWORD")}

if not credentials["username"] or not credentials["password"]:
    raise SystemExit("Set ADMIN_USERNAME and ADMIN_PASSWORD env vars before running.")

r = requests.post(f"{BASE}/login", json=credentials)
if r.status_code != 200:
    raise SystemExit(f"Login failed: {r.text}")

token = r.json()["access_token"]
print("Login OK.")

r = requests.get(f"{BASE}/alerts", headers={"Authorization": f"Bearer {token}"})
print(f"Alerts OK. Count: {len(r.json())}" if r.ok else f"Failed: {r.text}")