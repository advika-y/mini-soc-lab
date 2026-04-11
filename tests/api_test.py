import requests
import urllib3
import os

# Disable SSL warnings (self-signed cert)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Step 1: Login
login_url = "http://127.0.0.1:5000/login"

credentials = {
    "username": os.getenv("ADMIN_USERNAME"),
    "password": "admin123"
}
response = requests.post(login_url, json=credentials, verify=False)

if response.status_code == 200:
    token = response.json().get("access_token")
    print("TOKEN:", token)
else:
    print("Login failed:", response.text)
    exit()


# Step 2: Access protected route
headers = {
    "Authorization": f"Bearer {token}"
}

alerts_url = "http://127.0.0.1:5000/alerts"

response = requests.get(alerts_url, headers=headers, verify=False)

if response.status_code == 200:
    print("ALERTS:", response.json())
else:
    print("Failed to fetch alerts:", response.text)