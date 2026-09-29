#!/usr/bin/env python3
"""
CIPHERNEX-301 TELEMETRY DECRYPTION SCRIPT TEMPLATE
Ground Station 04 - Key Derivation & Manifest Recovery Module

TASK:
1. Supply the orbital inclination and epoch day recovered in Stage 1.
2. Supply the seed fragment carved from memory in Stage 3.
3. Execute this script to decrypt manifest.enc.
"""

import hashlib
import os
import subprocess
import sys

# =====================================================================
# [!] RECOVERED PARAMETERS - FILL IN THE BLANKS FROM STAGES 1 & 3
# =====================================================================
ORBITAL_INCLINATION = ""   # e.g., "11.11" (from Stage 1 TLE data)
ORBITAL_EPOCH       = ""   # e.g., "11.11" (from Stage 1 mission log)
SEED_FRAGMENT       = ""   # e.g., "xxxxxxxxxxx" (from Stage 3 memory dump)
# =====================================================================

def derive_keys(inclination: str, epoch: str, seed: str):
    """Weak Key Derivation Function (KDF) chaining orbital parameters."""
    salt_raw = f"{inclination}:{epoch}".encode("utf-8")
    salt = hashlib.sha256(salt_raw).hexdigest().encode("utf-8")
    
    # 32-byte AES Key and 16-byte IV represented in hex
    aes_key_hex = hashlib.sha256(seed.encode("utf-8") + salt).hexdigest()
    aes_iv_hex = hashlib.md5(salt).hexdigest()
    return aes_key_hex, aes_iv_hex

def decrypt_manifest(input_file="manifest.enc"):
    if not (ORBITAL_INCLINATION and ORBITAL_EPOCH and SEED_FRAGMENT):
        print("[-] Error: Missing required parameters.")
        print("    Edit kdf_generator.py and supply:")
        print("    - ORBITAL_INCLINATION (Stage 1)")
        print("    - ORBITAL_EPOCH       (Stage 1)")
        print("    - SEED_FRAGMENT       (Stage 3)")
        sys.exit(1)

    if not os.path.exists(input_file):
        print(f"[-] Error: Target file '{input_file}' not found in current folder.")
        sys.exit(1)

    key_hex, iv_hex = derive_keys(ORBITAL_INCLINATION, ORBITAL_EPOCH, SEED_FRAGMENT)
    
    try:
        result = subprocess.run([
            "openssl", "enc", "-d", "-aes-256-cbc",
            "-K", key_hex,
            "-iv", iv_hex,
            "-in", input_file
        ], capture_output=True, text=True, check=True)
        
        print("[+] Manifest Decryption Successful!\n")
        print(result.stdout)
    except subprocess.CalledProcessError:
        print("[-] Decryption failed.")
        print("    Verify that your orbital parameters and seed fragment are exact.")

if __name__ == "__main__":
    decrypt_manifest()
