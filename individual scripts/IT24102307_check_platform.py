import os
import sqlite3
import subprocess
import urllib.request

print("=" * 50)
print(" CIPHERNEX-301 // PLATFORM HEALTH CHECK")
print("=" * 50)

# 1. Verify Backend API is responding
try:
    with urllib.request.urlopen("http://127.0.0.1:5000/api/admin/overview", timeout=3) as res:
        print("[+] Backend API (Port 5000)   : ONLINE")
except Exception:
    print("[-] Backend API (Port 5000)   : OFFLINE (Run: python backend/server.py)")

# 2. Verify SQLite Database connectivity
db_path = os.path.join("backend", "ctf.db")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users;")
    user_count = cur.fetchone()[0]
    conn.close()
    print(f"[+] SQLite Database (ctf.db)  : CONNECTED ({user_count} registered users)")
else:
    print("[-] SQLite Database (ctf.db)  : MISSING")

# 3. Verify Stage 6 Docker Container status
try:
    check = subprocess.run(
        ["docker", "ps", "--filter", "name=stage6-box", "--format", "{{.Status}}"],
        capture_output=True, text=True
    )
    if "Up" in check.stdout:
        print("[+] Stage 6 Docker Sandbox    : RUNNING (Port 2222 active)")
    else:
        print("[-] Stage 6 Docker Sandbox    : STOPPED (Start container)")
except Exception:
    print("[-] Docker Daemon             : NOT RUNNING")

print("=" * 50)