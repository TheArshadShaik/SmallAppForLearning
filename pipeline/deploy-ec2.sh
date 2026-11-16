#!/bin/bash
# ==============================================================
# Continuous Deployment Script for AWS EC2
# Usage:
#   ./pipeline/deploy-ec2.sh [IMAGE_TAG] [PORT] [ENABLE_FEATURE_1] [ENABLE_FEATURE_2]
# Example:
#   ./pipeline/deploy-ec2.sh thearshadshaik/smallapp-server:latest 5000 true true
# ==============================================================
set -euo pipefail

APP_DIR="/opt/smallapp"
DOCKER_IMAGE="${1:-smallapp-server:latest}"
PORT="${2:-5000}"
FEATURE_1_ENABLED="${3:-true}"
FEATURE_2_ENABLED="${4:-true}"
CONTAINER_NAME="smallapp-production"

echo "=========================================================="
echo " Starting SmallApp Deployment to AWS EC2"
echo " Image:      ${DOCKER_IMAGE}"
echo " Port:       ${PORT}"
echo " Features:   Feature1=${FEATURE_1_ENABLED}, Feature2=${FEATURE_2_ENABLED}"
echo " Timestamp:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "=========================================================="

# Detect docker command (with or without sudo)
if docker info >/dev/null 2>&1; then
    DOCKER="docker"
elif sudo docker info >/dev/null 2>&1; then
    DOCKER="sudo docker"
else
    echo "ERROR: Docker is not running or current user does not have permission!"
    exit 1
fi

# Prepare target directory
mkdir -p "${APP_DIR}"
cd "${APP_DIR}"

# 1. Pull latest image from Docker Hub
echo "==> Pulling Docker image: ${DOCKER_IMAGE}..."
${DOCKER} pull "${DOCKER_IMAGE}"

# 2. Stop and remove existing container if running
if [ "$(${DOCKER} ps -aq -f name=${CONTAINER_NAME})" ]; then
    echo "==> Stopping and removing existing ${CONTAINER_NAME} container..."
    ${DOCKER} stop "${CONTAINER_NAME}" || true
    ${DOCKER} rm "${CONTAINER_NAME}" || true
fi

# 3. Start new container
echo "==> Starting new container on host ports 80 and ${PORT}..."
${DOCKER} run -d \
    --name "${CONTAINER_NAME}" \
    --restart unless-stopped \
    -p 80:5000 \
    -p "${PORT}:5000" \
    -e FLASK_ENV=production \
    -e PORT=5000 \
    -e ENABLE_FEATURE_1="${FEATURE_1_ENABLED}" \
    -e ENABLE_FEATURE_2="${FEATURE_2_ENABLED}" \
    "${DOCKER_IMAGE}"

# 4. Verify deployment health with retry loop
echo "==> Verifying container health on http://localhost:5000/health..."
sleep 5
HEALTH_SUCCESS=0
MAX_ATTEMPTS=10

for i in $(seq 1 $MAX_ATTEMPTS); do
    if curl -s -f http://localhost:5000/health | grep -q "healthy"; then
        echo "==> Health check PASSED on attempt $i!"
        HEALTH_SUCCESS=1
        break
    else
        echo "Waiting for service to become healthy... ($i/$MAX_ATTEMPTS)"
        sleep 3
    fi
done

if [ $HEALTH_SUCCESS -eq 0 ]; then
    echo "==> ERROR: Health check failed after $MAX_ATTEMPTS attempts!"
    ${DOCKER} logs "${CONTAINER_NAME}"
    exit 1
fi

echo "=========================================================="
echo " SmallApp successfully deployed and running on AWS EC2!"
echo " Access URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || hostname -I | awk '{print $1}')/"
echo "=========================================================="

