import struct
import sys
import os

pcap_path = os.path.join("challenges", "stage2", "telemetry_burst.pcap")
if not os.path.exists(pcap_path):
    pcap_path = "telemetry_burst.pcap"

print("[*] Reassembling Stage 2 telemetry packets...")

if not os.path.exists(pcap_path):
    print(f"[-] PCAP file not found: {pcap_path}")
    sys.exit(1)

fragments = {}

with open(pcap_path, "rb") as f:
    f.read(24)  # Skip 24-byte PCAP global header
    while True:
        pkt_hdr = f.read(16)
        if len(pkt_hdr) < 16:
            break
        incl_len = struct.unpack("<I", pkt_hdr[8:12])[0]
        data = f.read(incl_len)

        # Check for IPv4 UDP packet targeting destination port 4000
        if len(data) >= 42 and struct.unpack(">H", data[36:38])[0] == 4000:
            payload = data[42:]
            seq_num = struct.unpack(">I", payload[:4])[0]
            fragments[seq_num] = payload[4:]

# Sort fragments by sequence number and join
assembled = b"".join(fragments[seq] for seq in sorted(fragments.keys()))
print("\n[+] Recovered Telemetry Payload:")
print(assembled.decode(errors="ignore"))