#!/usr/bin/env python3
import math
import os
import struct
import subprocess
import sys
import wave

def generate_wav(filename="downlink_carrier.wav", duration=5, sample_rate=44100):
    """Generates a synthetic VHF carrier tone with telemetry modulation."""
    num_samples = duration * sample_rate
    carrier_freq = 1200.0   # Main subcarrier frequency (Hz)
    mod_freq = 2200.0       # Telemetry audio frequency shift (Hz)
    
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)      # Mono
        wav.setsampwidth(2)      # 16-bit
        wav.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Synthesize dual-tone telemetry subcarrier
            sample = 0.6 * math.sin(2.0 * math.pi * carrier_freq * t)
            sample += 0.3 * math.sin(2.0 * math.pi * mod_freq * t)
            sample += 0.1 * math.sin(2.0 * math.pi * 4800.0 * t)  # High-frequency noise
            
            int_sample = int(sample * 32767.0)
            frames.extend(struct.pack('<h', int_sample))
            
        wav.writeframes(frames)
    print(f"[+] Created synthetic carrier: {filename}")

def build_stage5():
    # 1. Ensure steghide is installed
    if subprocess.call(["which", "steghide"], stdout=subprocess.DEVNULL) != 0:
        print("[*] Installing steghide...")
        subprocess.check_call(["sudo", "apt", "update"])
        subprocess.check_call(["sudo", "apt", "install", "-y", "steghide"])

    # 2. Build base audio wave
    wav_file = "downlink_carrier.wav"
    generate_wav(wav_file)

    # 3. Create covert payload file
    payload_file = "stego_payload.txt"
    payload_text = (
        "[CIPHERNEX-301 COVERT PAYLOAD EXTRACTION]\n"
        "=========================================\n"
        "TRANSMISSION : DOWNLINK CARRIER 145.825 MHz\n"
        "STAGE 5 FLAG : CIPHERNEX{audio_subcarrier_stego_recovered}\n"
        "\n"
        "[TARGET INFRASTRUCTURE CREDENTIALS]\n"
        "HOST         : 127.0.0.1 (Internal Relay Container)\n"
        "SSH PORT     : 2222\n"
        "USERNAME     : ground-user\n"
        "PASSWORD     : SatTrack#2024!Ops\n"
        "NOTE         : Scheduled telemetry maintenance task runs every 60s.\n"
        "=========================================\n"
    )
    with open(payload_file, "w") as f:
        f.write(payload_text)

    # 4. Embed secret payload using Stage 3 Passphrase
    passphrase = "N0rthSt4r_St3g0_K3y!99"
    cmd = [
        "steghide", "embed",
        "-cf", wav_file,
        "-ef", payload_file,
        "-p", passphrase,
        "-f"
    ]
    subprocess.run(cmd, check=True)
    
    # Clean up plaintext payload file
    if os.path.exists(payload_file):
        os.remove(payload_file)

    print(f"[+] Stage 5 setup complete. '{wav_file}' is ready for distribution.")

if __name__ == "__main__":
    build_stage5()