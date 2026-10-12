import struct
import base64
import re

pcap = "telemetry_burst.pcap"
frames = {}

with open(pcap, "rb") as f:
    header = f.read(24)

    magic = header[:4]

    if magic == b"\xd4\xc3\xb2\xa1":
        endian = "<"
    elif magic == b"\xa1\xb2\xc3\xd4":
        endian = ">"
    else:
        raise ValueError("Unsupported PCAP byte order")

    while True:
        h = f.read(16)

        if len(h) < 16:
            break

        size = struct.unpack(endian + "I", h[8:12])[0]
        d = f.read(size)

        if len(d) < 42 or d[12:14] != b"\x08\x00":
            continue

        ip = 14

        if d[ip + 9] != 17:  # UDP
            continue

        off = ip + (d[ip] & 15) * 4

        if len(d) < off + 8:
            continue

        src, dst, length, _ = struct.unpack(
            ">HHHH", d[off:off + 8]
        )

        if dst != 4000:
            continue

        payload = d[off + 8:min(len(d), off + length)]

        match = re.match(rb"FRAME:(\d+):(.*)", payload)

        if match:
            number = int(match.group(1))
            content = match.group(2)
            frames[number] = content

print("Frames captured:", len(frames))

# Recover the flag from Frames 1-5
flag_b64 = b"".join(
    frames[n] for n in sorted(frames) if n <= 5
)

print("Flag Base64:", flag_b64.decode())

flag = base64.b64decode(
    flag_b64, validate=True
).decode()

print("Recovered flag:", flag)

# Decode Frame 6 separately as telemetry
if 6 in frames:
    telemetry = base64.b64decode(
        frames[6], validate=True
    ).decode()

    print("Telemetry:", telemetry)