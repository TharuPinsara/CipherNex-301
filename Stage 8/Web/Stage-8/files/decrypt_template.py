#!/usr/bin/env python3
"""
CipherNex-301 // Stage 8 Automated Decryption Pipeline
"""
import sys
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

ENCRYPTED_ARCHIVE = "Files/core_mission.enc"

# Participant-provided parameters from Stages 1-7
PARAMS = {
    "FREQ": "XXXXXXXX",
    "SEED": "XXXXXXXX",
    "INCLINATION": "XXXXXXXX",
    "C2_KEY": "XXXXXXXXX",
    "AUTH_TOKEN": "XXXXXXXX"
}

try:
    with open(ENCRYPTED_ARCHIVE, "rb") as f:
        file_bytes = f.read()
except FileNotFoundError:
    print(f"[-] Missing archive: {ENCRYPTED_ARCHIVE}")
    sys.exit(1)

salt = file_bytes[:16]
iv = file_bytes[16:32]
ciphertext = file_bytes[32:]

print("[*] Synthesizing recovered parameters...")
composite_secret = f"{PARAMS['FREQ']}:{PARAMS['SEED']}:{PARAMS['INCLINATION']}:{PARAMS['C2_KEY']}:{PARAMS['AUTH_TOKEN']}".encode("utf-8")

print("[*] Computing PBKDF2-HMAC-SHA256 key material (100,000 rounds)...")
derived_material = hashlib.pbkdf2_hmac(
    "sha256",
    composite_secret,
    salt,
    iterations=100000,
    dklen=48
)

key = derived_material[:32]
expected_iv = derived_material[32:48]

if iv != expected_iv:
    print("[-] Warning: File IV header mismatch. Using IV from archive header.")

try:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_plain = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plain) + unpadder.finalize()
    
    print("\n--- DECRYPTED MISSION ARCHIVE ---")
    print(plaintext.decode("utf-8"))
    print("---------------------------------")
    
    for line in plaintext.decode("utf-8").splitlines():
        if "CIPHERNEX{" in line:
            print(f"[✓] CAPSTONE FLAG RECOVERED: {line.split(': ')[-1].strip()}")
except Exception as err:
    print(f"[-] Decryption failed: {err}")
    print("[!] Verify that all parameter values match their exact case and formatting.")
