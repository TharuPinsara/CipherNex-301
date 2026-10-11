#!/usr/bin/env python3
"""
CipherNex-301 - Stage 7 C2 solver.

Usage:
    python3 solve_c2.py                      # looks for the two pcaps in the current folder
    python3 solve_c2.py file1.pcap file2.pcap

No extra libraries needed (pure Python 3).
"""
import re
import struct
import sys

PORT = 9043
KEY = bytes.fromhex("9A4F7C2B1E8D")


def read_pcap(path):
    """Yield raw packet bytes from a classic .pcap file."""
    data = open(path, "rb").read()
    magic = data[:4]
    if magic in (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1"):
        endian = "<"
    elif magic in (b"\xa1\xb2\xc3\xd4", b"\xa1\xb2\x3c\x4d"):
        endian = ">"
    else:
        sys.exit(f"{path}: not a classic pcap file")
    offset = 24  # skip global header
    while offset + 16 <= len(data):
        incl_len = struct.unpack(endian + "I", data[offset + 8:offset + 12])[0]
        offset += 16  # skip per-packet header
        yield data[offset:offset + incl_len]
        offset += incl_len


def tcp_payload(frame):
    """Return (dst_port, payload) for an Ethernet/IPv4/TCP frame, else None."""
    if len(frame) < 54 or frame[12:14] != b"\x08\x00":  # Ethernet + IPv4 only
        return None
    ip = frame[14:]
    if ip[9] != 6:  # not TCP
        return None
    ihl = (ip[0] & 0x0F) * 4
    tcp = ip[ihl:]
    dst_port = struct.unpack(">H", tcp[2:4])[0]
    data_off = (tcp[12] >> 4) * 4
    return dst_port, tcp[data_off:]


def main():
    files = sys.argv[1:] or ["c2_stream_01.pcap", "c2_stream_02.pcap"]

    # Steps 1-2: read BOTH captures, keep only data segments to port 9043
    chunks = {}
    for f in files:
        for frame in read_pcap(f):
            parsed = tcp_payload(frame)
            if not parsed:
                continue
            port, payload = parsed
            if port != PORT or len(payload) <= 8:
                continue
            # Step 3: 4-byte big-endian sequence index + 4-byte length
            seq, length = struct.unpack(">II", payload[:8])
            chunks[seq] = payload[8:8 + length]

    if not chunks:
        sys.exit("No data packets to port 9043 found.")

    # Step 4: order by sequence index, check nothing is missing
    order = sorted(chunks)
    missing = [i for i in range(order[-1] + 1) if i not in chunks]
    print(f"[+] Chunks found: {len(order)} (indices {order[0]}..{order[-1]})")
    if missing:
        print(f"[!] Missing chunk indices: {missing}")

    # Step 5: concatenate the ciphertext slices
    ciphertext = b"".join(chunks[i] for i in order)
    print(f"[+] Ciphertext length: {len(ciphertext)} bytes")

    # Step 6: repeating 6-byte XOR, key runs continuously across the stream
    plaintext = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(ciphertext))
    text = plaintext.decode(errors="replace")

    print("\n----- Decrypted command chain -----")
    print(text)
    print("-----------------------------------")

    flag = re.search(r"CIPHERNEX\{[^}]*\}", text)
    token = re.search(r"NX-ALPHA-\d+", text)
    if flag:
        print(f"\n[FLAG]  {flag.group(0)}")
    if token:
        print(f"[TOKEN] {token.group(0)}  (keep for Stage 8)")


if __name__ == "__main__":
    main()
