
import os
import re
import shutil
import subprocess
from pathlib import Path

print("=" * 55)
print(" CIPHERNEX-301 // STAGE 5: HIDDEN IN THE NOISE")
print("=" * 55)

# Locate the Stage 5 challenge directory
BASE_DIR = Path(__file__).resolve().parent
WAV_FILE = BASE_DIR / "downlink_carrier.wav"
OUTPUT_FILE = BASE_DIR / "stego_payload.bin"

# Check whether the required tools and files are available
if shutil.which("steghide") is None:
    print("[-] Steghide is not installed or not in PATH.")
    print("[*] Install Steghide before running this solver.")
    raise SystemExit(1)

if not WAV_FILE.is_file():
    print(f"[-] WAV file not found: {WAV_FILE}")
    raise SystemExit(1)

print(f"[*] Challenge file: {WAV_FILE.name}")

# Get the passphrase discovered from Stage 3
passphrase = input("Enter the passphrase recovered from Stage 3: ")

if not passphrase:
    print("[-] Passphrase cannot be empty.")
    raise SystemExit(1)

# Extract the hidden artifact from the WAV file
print("[*] Extracting the hidden payload...")

try:
    result = subprocess.run(
        [
            "steghide",
            "extract",
            "-sf", str(WAV_FILE),
            "-p", passphrase,
            "-xf", str(OUTPUT_FILE),
            "-f"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
except subprocess.TimeoutExpired:
    print("[-] Extraction timed out.")
    raise SystemExit(1)

if result.returncode != 0:
    print("[-] Extraction failed. Check the Stage 3 passphrase.")
    if result.stderr.strip():
        print(result.stderr.strip())
    elif result.stdout.strip():
        print(result.stdout.strip())
    raise SystemExit(1)

if not OUTPUT_FILE.is_file():
    print("[-] Extraction finished, but the payload file was not created.")
    raise SystemExit(1)

print(f"[+] Extracted artifact: {OUTPUT_FILE.name}")

# Search the extracted artifact for a flag
print("[*] Searching the extracted artifact for the Stage 5 flag...")

try:
    data = OUTPUT_FILE.read_bytes()
except OSError as error:
    print(f"[-] Could not read the extracted artifact: {error}")
    raise SystemExit(1)

# Find the expected CTF flag format in the artifact bytes
matches = re.findall(rb"CIPHERNEX\{[A-Za-z0-9_-]+\}", data)

print(f"[*] Artifact size: {len(data)} bytes")

if matches:
    flag = matches[0].decode("ascii")
    print("\n[+] STAGE 5 FLAG RECOVERED")
    print("-" * 55)
    print(flag)
    print("-" * 55)
else:
    print("[-] No flag matching the expected format was found.")
    print("[*] Inspect the artifact; the flag may be encoded or stored differently.")

print("=" * 55)
