#!/bin/bash
# ==============================================================
# AWS EC2 User-Data Bootstrap Script
# Supports: Ubuntu 22.04 / 24.04 LTS & Amazon Linux 2023
# Purpose: Zero-touch setup of Docker, Git, and SmallApp container
# ==============================================================
set -euo pipefail

exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "==> Starting SmallApp EC2 Provisioning..."

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS="unknown"
fi

echo "==> Detected OS: $OS"

if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get update -y
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release git

    # Install Docker
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Enable and start Docker
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ubuntu || true

elif [ "$OS" = "amzn" ]; then
    dnf update -y
    dnf install -y docker git
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ec2-user || true
fi

# Create app directory
mkdir -p /opt/smallapp
cd /opt/smallapp

# Optional: Clone repo or pull pre-built Docker image from Docker Hub / ECR / ACR
echo "==> Setting up deployment script..."
cat << 'EOF' > /opt/smallapp/start.sh
#!/bin/bash
set -e
PORT=${PORT:-5000}
IMAGE_NAME=${DOCKER_IMAGE:-"smallapp-server:latest"}

echo "Deploying SmallApp on port ${PORT}..."
docker stop smallapp-running 2>/dev/null || true
docker rm smallapp-running 2>/dev/null || true

# Run container
docker run -d \
  --name smallapp-running \
  --restart unless-stopped \
  -p ${PORT}:5000 \
  -e FLASK_ENV=production \
  -e ENABLE_FEATURE_1=true \
  -e ENABLE_FEATURE_2=true \
  ${IMAGE_NAME}

# Wait and verify health
sleep 5
curl -f http://localhost:${PORT}/health || { echo "Health check failed!"; exit 1; }
echo "Deployment successful!"
EOF

chmod +x /opt/smallapp/start.sh
echo "==> EC2 Bootstrap Completed Successfully!"
