#!/bin/bash
# ==============================================================
# Automated Testing & Coverage Script for Azure Pipelines & Local
# ==============================================================
set -euo pipefail

echo "==> Setting up Python test environment..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

mkdir -p test-results

echo "==> Executing PyTest test suite with coverage instrumentation..."
pytest \
  --junitxml=test-results/junit-test-results.xml \
  --cov=app \
  --cov-report=xml:coverage.xml \
  --cov-report=html:htmlcov \
  tests/

echo "==> All automated tests executed successfully!"

