#!/bin/bash
# ==============================================================
# Container Health Smoke Test Script
# Usage: ./pipeline/smoke-test.sh [IMAGE_TAG]
# ==============================================================
set -euo pipefail

IMAGE_TAG="${1:-smallapp-server:latest}"
CONTAINER_NAME="test-health-container"

echo "==> Running container smoke test for image: ${IMAGE_TAG}"

# Stop any lingering container with the same name
docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true

# Start container temporarily on port 5000
docker run -d --name "${CONTAINER_NAME}" -p 5000:5000 "${IMAGE_TAG}"

# Allow Gunicorn worker to initialize
sleep 5

# Probe health endpoint
if curl -s -f http://localhost:5000/health | grep -q "healthy"; then
    echo "==> Smoke test PASSED: Container is healthy and responding!"
    docker stop "${CONTAINER_NAME}"
    docker rm "${CONTAINER_NAME}"
    exit 0
else
    echo "==> ERROR: Container health check failed!"
    docker logs "${CONTAINER_NAME}"
    docker rm -f "${CONTAINER_NAME}"
    exit 1
fi

