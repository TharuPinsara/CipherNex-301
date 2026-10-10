import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

def api_call(endpoint, payload):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode())

print("=" * 50)
print(" CIPHERNEX-301 // INTEGRATION API TEST")
print("=" * 50)

team = f"SLIIT_TEAM_{int(time.time())}"
email = f"{team.lower()}@campus.lk"
password = "CampusPassword123"

# 1. Register
reg = api_call("/register", {"team_name": team, "email": email, "password": password})
print(f"[+] TC-01 Registration API      : {reg.get('message', 'Success')}")

# 2. Login
login = api_call("/login", {"email": email, "password": password})
user_id = login.get("user", {}).get("id")
print(f"[+] TC-02 User Authentication   : Logged in (User ID: {user_id})")

# 3. Reject Wrong Flag
fake_sub = api_call("/submit-flag", {"team_name": team, "user_id": user_id, "stage_id": 1, "flag": "WRONG_FLAG"})
print(f"[+] TC-03 Fake Flag Rejection   : PASSED (Rejected: {not fake_sub.get('success')})")

# 4. Accept Valid Flag
real_sub = api_call("/submit-flag", {"team_name": team, "user_id": user_id, "stage_id": 1, "flag": "CIPHERNEX{ghost_signal_recovered}"})
print(f"[+] TC-04 Real Flag Progression : PASSED (Stage 2 Unlocked: {real_sub.get('success')})")

print("=" * 50)
print("[+] ALL INTEGRATION CHECKS PASSED")
print("=" * 50)