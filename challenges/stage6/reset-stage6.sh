#!/bin/bash
# ==============================================================================
# CipherNex-301 // Stage 6 Sandbox Auto-Recovery
# ==============================================================================
set -e

CONTAINER_NAME="stage6-box"
IMAGE_NAME="stage6-serviceghost"
BUILD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[*] Tearing down existing Stage 6 container..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

echo "[*] Building fresh Docker image from $BUILD_DIR..."
docker build -t "$IMAGE_NAME" "$BUILD_DIR"

echo "[*] Deploying unprivileged Stage 6 container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -p 2222:22 \
    --memory="512m" \
    --cpus="1.0" \
    "$IMAGE_NAME"

echo "[+] Stage 6 container restored and active on port 2222."