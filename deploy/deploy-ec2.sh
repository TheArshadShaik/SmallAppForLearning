#!/bin/bash
# ==============================================================
# Continuous Deployment Script for AWS EC2
# Executed via Azure DevOps Pipeline (SSH Task) or Manual Trigger
# ==============================================================
set -euo pipefail

APP_DIR="/opt/smallapp"
DOCKER_IMAGE="${1:-smallapp-server:latest}"
PORT="${2:-5000}"
FEATURE_1_ENABLED="${3:-true}"
FEATURE_2_ENABLED="${4:-true}"

echo "=========================================================="
echo " Starting SmallApp Deployment to AWS EC2"
echo " Image:   ${DOCKER_IMAGE}"
echo " Port:    ${PORT}"
echo " Features: Feature1=${FEATURE_1_ENABLED}, Feature2=${FEATURE_2_ENABLED}"
echo "=========================================================="

# Create target directory
mkdir -p "${APP_DIR}"
cd "${APP_DIR}"

# Login to registry if credentials provided in environment
if [ -n "${REGISTRY_SERVER:-}" ] && [ -n "${REGISTRY_USER:-}" ] && [ -n "${REGISTRY_PASSWORD:-}" ]; then
    echo "Logging into container registry ${REGISTRY_SERVER}..."
    echo "${REGISTRY_PASSWORD}" | docker login "${REGISTRY_SERVER}" -u "${REGISTRY_USER}" --password-stdin
    docker pull "${DOCKER_IMAGE}"
fi

# Stop and remove existing container
if [ "$(docker ps -aq -f name=smallapp-production)" ]; then
    echo "Stopping existing container..."
    docker stop smallapp-production || true
    docker rm smallapp-production || true
fi

# Run new container
echo "Starting new container..."
docker run -d \
    --name smallapp-production \
    --restart unless-stopped \
    -p 80:5000 \
    -p ${PORT}:5000 \
    -e FLASK_ENV=production \
    -e PORT=5000 \
    -e ENABLE_FEATURE_1="${FEATURE_1_ENABLED}" \
    -e ENABLE_FEATURE_2="${FEATURE_2_ENABLED}" \
    "${DOCKER_IMAGE}"

# Verify container health check
echo "Verifying deployment health..."
HEALTH_CHECK_MAX_RETRIES=10
HEALTH_CHECK_SUCCESS=0

for i in $(seq 1 $HEALTH_CHECK_MAX_RETRIES); do
    if curl -s -f http://localhost:5000/health | grep -q "healthy"; then
        echo "Health check PASSED on attempt $i!"
        HEALTH_CHECK_SUCCESS=1
        break
    else
        echo "Waiting for service to be healthy... ($i/$HEALTH_CHECK_MAX_RETRIES)"
        sleep 3
    fi
done

if [ $HEALTH_CHECK_SUCCESS -eq 0 ]; then
    echo "ERROR: Health check failed after $HEALTH_CHECK_MAX_RETRIES attempts!"
    docker logs smallapp-production
    exit 1
fi

echo "=========================================================="
echo " SmallApp successfully deployed and operational on AWS EC2!"
echo " Access URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || hostname -I | awk '{print $1}')/"
echo "=========================================================="
