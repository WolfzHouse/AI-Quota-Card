import requests

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
print(f"Login Cookies: {session.cookies.get_dict()}")
print(f"Login Headers: {dict(login_response.headers)}")
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
print(f"Providers Response: {providers_response.text[:500]}")
print(f"Session Cookies: {session.cookies.get_dict()}")
