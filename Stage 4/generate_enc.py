import hashlib
import os

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
except ImportError:
    # Fallback to standard cryptography library if pycryptodome is not installed
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pycryptodome"])
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad

def build_stage4_artifacts():
    # 1. Cryptographic inputs derived from prior stages
    # Stage 1 Orbital parameters: Inclination = 51.64, Epoch Day = 24256.41738426
    # Stage 3 Seed Fragment = 7a8e2b9c1d0f
    INCLINATION = "51.64"
    EPOCH_DAY = "24256.41738426"
    SEED_FRAGMENT = "7a8e2b9c1d0f"

    # Weak KDF Formulation:
    # Salt = SHA256(Inclination:Epoch_Day)
    # Key  = SHA256(Seed_Fragment + Salt)[:32] (AES-256)
    # IV   = MD5(Salt)[:16]                    (AES-CBC block size)
    salt_raw = f"{INCLINATION}:{EPOCH_DAY}".encode("utf-8")
    salt = hashlib.sha256(salt_raw).hexdigest().encode("utf-8")
    
    key = hashlib.sha256(SEED_FRAGMENT.encode("utf-8") + salt).digest()
    iv = hashlib.md5(salt).digest()

    # 2. Manifest Plaintext Payload
    plaintext_manifest = (
        b"[CIPHERNEX-301 ORBITAL TELEMETRY MANIFEST]\n"
        b"==========================================\n"
        b"SECURITY LEVEL : CONFIDENTIAL // ORBITAL RESTRICTED\n"
        b"STAGE 4 FLAG   : CIPHERNEX{orbital_telemetry_manifest_decrypted}\n"
        b"CARRIER LINK   : downlink_carrier.wav (VHF 145.825 MHz)\n"
        b"MODULATION     : Audio Subcarrier / Steganographic Overlay\n"
        b"SSH TARGET     : ground-user @ 127.0.0.1:2222\n"
        b"STATUS         : ADVERSARY C2 INJECTION DETECTED\n"
        b"==========================================\n"
    )

    # 3. Encrypt via AES-256-CBC
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext_manifest, AES.block_size))

    with open("manifest.enc", "wb") as f:
        f.write(ciphertext)

    # 4. Generate participant template script: kdf_generator.py
    kdf_template = '''#!/usr/bin/env python3
"""
CIPHERNEX-301 TELEMETRY DECRYPTION SCRIPT TEMPLATE
Ground Station 04 - Key Derivation & Manifest Recovery Module

TASK:
1. Supply the orbital inclination and epoch day recovered in Stage 1.
2. Supply the seed fragment carved from memory in Stage 3.
3. Execute this script to decrypt manifest.enc.
"""

import hashlib
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# =====================================================================
# [!] RECOVERED PARAMETERS - FILL IN THE BLANKS FROM STAGES 1 & 3
# =====================================================================
ORBITAL_INCLINATION = ""   # e.g., "XX.XX" (from Stage 1 TLE data)
ORBITAL_EPOCH       = ""   # e.g., "24256.XXXXXXXX" (from Stage 1 mission log)
SEED_FRAGMENT       = ""   # e.g., "7a8e..." (from Stage 3 memory dump)
# =====================================================================

def derive_keys(inclination: str, epoch: str, seed: str):
    """Weak Key Derivation Function (KDF) chaining orbital parameters."""
    salt_raw = f"{inclination}:{epoch}".encode("utf-8")
    salt = hashlib.sha256(salt_raw).hexdigest().encode("utf-8")
    
    # AES-256 Key (32 bytes) & CBC IV (16 bytes)
    aes_key = hashlib.sha256(seed.encode("utf-8") + salt).digest()
    aes_iv = hashlib.md5(salt).digest()
    return aes_key, aes_iv

def decrypt_manifest(input_file="manifest.enc"):
    if not (ORBITAL_INCLINATION and ORBITAL_EPOCH and SEED_FRAGMENT):
        print("[-] Error: Missing required orbital or seed parameters.")
        print("    Check findings from Stage 1 (OSINT) and Stage 3 (Forensics).")
        sys.exit(1)

    key, iv = derive_keys(ORBITAL_INCLINATION, ORBITAL_EPOCH, SEED_FRAGMENT)
    
    try:
        with open(input_file, "rb") as f:
            ciphertext = f.read()
            
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        print("[+] Manifest Decryption Successful!\\n")
        print(decrypted.decode("utf-8"))
    except Exception as e:
        print(f"[-] Decryption failed: {e}")
        print("    Verify that your orbital parameters and seed fragment are exact.")

if __name__ == "__main__":
    decrypt_manifest()
'''

    with open("kdf_generator.py", "w") as f:
        f.write(kdf_template)

    print("[+] Successfully generated Stage 4 challenge files:")
    print("    - manifest.enc (Encrypted payload)")
    print("    - kdf_generator.py (Participant KDF template)")

if __name__ == "__main__":
    build_stage4_artifacts()