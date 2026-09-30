import os
import struct

def generate_memory_dump(filename="ground_station.raw", size_mb=16):
    total_bytes = size_mb * 1024 * 1024
    
    # Base synthetic memory buffer (simulated kernel & userland noise)
    print(f"[*] Allocating {size_mb} MB memory buffer...")
    buffer = bytearray(os.urandom(total_bytes))
    
    # 1. Inject simulated Linux kernel & system process artifacts
    system_noise = [
        b"Linux version 6.8.0-31-generic (buildd@lcy02-amd64-004) #31-Ubuntu SMP PREEMPT_DYNAMIC",
        b"BOOT_IMAGE=/boot/vmlinuz-6.8.0-31-generic root=UUID=74a12b48-18e3-4f91 ro quiet splash",
        b"/lib/systemd/systemd --system --deserialize=34",
        b"[kworker/u16:0-events_unbound]",
        b"/usr/sbin/cron -f -P",
        b"/usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation",
        b"/usr/sbin/rsyslogd -n -iNONE",
        b"/usr/sbin/sshd -D [listener] 0 of 10-100 startups",
        b"gnome-terminal-server --class=Gnome-terminal",
        b"USER=operator HOME=/home/operator SHELL=/bin/bash TERM=xterm-256color"
    ]
    
    for idx, noise in enumerate(system_noise):
        offset = (idx + 1) * 256 * 1024 + 1024
        buffer[offset:offset + len(noise)] = noise

    # 2. Inject target process volatile structure (cnx-telemetry-daemon, PID 1942)
    # This matches the daemon identified in Stage 2 Frame 06
    target_offset = 4 * 1024 * 1024 + 512  # Positioned at 4MB mark
    
    cmdline_payload = (
        b"/usr/local/bin/cnx-telemetry-daemon\x00"
        b"--sync\x00"
        b"--port=4000\x00"
        b"--pid=1942\x00"
        b"--flag=CIPHERNEX{volatile_memory_forensics_extracted}\x00"
        b"--seed-fragment=7a8e2b9c1d0f\x00"
        b"--audio-pass=N0rthSt4r_St3g0_K3y!99\x00"
    )
    
    process_env_block = (
        b"DAEMON_NAME=cnx-telemetry-daemon\n"
        b"STATUS=SYNC_STREAM_PORT_4000\n"
        b"TELEMETRY_SOURCE=CIPHERNEX-301\n"
        b"BUFFER_DUMP=INITIATED_CRASH_CAPTURE\n"
    )
    
    # Write target payload into allocated process memory region
    buffer[target_offset:target_offset + len(cmdline_payload)] = cmdline_payload
    buffer[target_offset + 1024:target_offset + 1024 + len(process_env_block)] = process_env_block
    
    # 3. Write out to disk
    with open(filename, "wb") as f:
        f.write(buffer)
        
    print(f"[+] Successfully generated: {filename} ({os.path.getsize(filename):,} bytes)")

if __name__ == "__main__":
    generate_memory_dump()