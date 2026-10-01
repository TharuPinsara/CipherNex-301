#!/bin/bash
set -e

# Ensure clean logging directory
mkdir -p /var/log /opt/orbital-sync
touch /var/log/orbital-sync.log
chmod 666 /var/log/orbital-sync.log

# Ensure target script exists and has world-writable permissions
chmod 777 /opt/orbital-sync/sync_job.sh

# Generate host keys if not present
ssh-keygen -A

# Start SSH daemon
/usr/sbin/sshd

echo "[+] CipherNex-301 Stage 6 container online on SSH port 22."
echo "[*] Periodic root trigger loop running every 30 seconds..."

# Loop mimicking root systemd timer trigger
while true; do
    sleep 30
    if [ -f "/opt/orbital-sync/sync_job.sh" ]; then
        /bin/bash /opt/orbital-sync/sync_job.sh >/dev/null 2>&1 || true
    fi
done