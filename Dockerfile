# ==============================================================
# SmallApp Modular Python Server - Multi-Stage Production Dockerfile
# Supports Monolithic Master, Feature 1 Microservice, or Feature 2 Microservice
# ==============================================================

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    FLASK_ENV=production

WORKDIR /app

# Install system dependencies (curl for container healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies in a dedicated layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-privileged user for security compliance
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# Copy application source code
COPY app/ app/
COPY run.py .
COPY pytest.ini .

# Set ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Container Healthcheck (polled by Docker & AWS ALB/ECS)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Default Command: Run unified master application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--threads", "2", "--timeout", "60", "run:app"]
