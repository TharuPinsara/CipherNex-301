import os
import re
import base64

print("=" * 50)
print(" CIPHERNEX-301 // STAGE 5 TELEMETRY LOG DECODER")
print("=" * 50)

# Resolve path to challenge artifact
log_path = os.path.join("challenges", "stage5", "telemetry.log")
if not os.path.exists(log_path):
    log_path = "telemetry.log"

if not os.path.exists(log_path):
    print(f"[-] Telemetry log not found: {log_path}")
    print("[*] Create 'challenges/stage5/telemetry.log' to test.")
    exit(1)

print(f"[*] Scanning {log_path} for anomalous frames...")

recovered_chunks = []

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        # Identify lines containing anomalous satellite subsystem broadcasts
        if "[SUBSYS_ANOMALY]" in line:
            match = re.search(r"PAYLOAD:([A-Za-z0-9+/=]+)", line)
            if match:
                raw_b64 = match.group(1)
                try:
                    chunk = base64.b64decode(raw_b64).decode("utf-8", errors="ignore")
                    recovered_chunks.append(chunk)
                except Exception:
                    pass

print(f"[+] Intercepted {len(recovered_chunks)} valid payload frames.")

# Assemble the decoded telemetry chunks in sequential order
recovered_message = "".join(recovered_chunks)

print("\n[+] Reassembled Transmission:")
print("-" * 50)
print(recovered_message)
print("-" * 50)

if "CIPHERNEX{" in recovered_message:
    start = recovered_message.find("CIPHERNEX{")
    end = recovered_message.find("}", start) + 1
    flag = recovered_message[start:end]
    print(f"\n[+] RECOVERED STAGE 5 FLAG: {flag}")
else:
    print("[-] Flag token not identified in parsed buffer.")

print("=" * 50)