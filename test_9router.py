import requests
import json

# Test 9router authentication
base_url = "http://192.168.1.107:20128"
password = "TD7355608"

# Create session to persist cookies
session = requests.Session()

# Step 1: Login
print("Step 1: Attempting login...")
login_response = session.post(
    f"{base_url}/api/auth/login",
    json={"password": password},
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
)

print(f"Login Status: {login_response.status_code}")
print(f"Login Response: {login_response.text}")
print()

# Step 2: Get providers
print("Step 2: Fetching providers...")
providers_response = session.get(
    f"{base_url}/api/providers/client",
    headers={
        "Accept": "application/json"
    }
)

print(f"Providers Status: {providers_response.status_code}")
providers_data = providers_response.json()
print(f"\nFull Response:")
print(json.dumps(providers_data, indent=2))

print(f"\n\nConnections Summary:")
for i, conn in enumerate(providers_data.get("connections", [])):
    print(f"\n[{i}] Provider: {conn.get('provider')}")
    print(f"    Name: {conn.get('name')}")
    print(f"    Email: {conn.get('email')}")
    print(f"    Active: {conn.get('isActive')}")
    print(f"    ID: {conn.get('id')}")
