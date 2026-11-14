# SmallApp: Modular Python Server with Isolated Feature Microservices

[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.14-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests Passing](https://img.shields.io/badge/tests-14%20passed-brightgreen.svg)]()
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue.svg)]()
[![Azure DevOps CI/CD](https://img.shields.io/badge/Azure%20DevOps-CI%2FCD-0078D7.svg)]()
[![AWS EC2](https://img.shields.io/badge/AWS-EC2-FF9900.svg)]()

SmallApp is a modular Python web application built using **Flask 3.x**, **Gunicorn**, and **Docker**.

It features:
1. **Home Page (`/`)**: Main feature and master gateway/dashboard.
2. **Feature 1 (`/feature1`)**: Single-page Cloud Sizing & Cost Estimator with dedicated REST API.
3. **Feature 2 (`/feature2`)**: System Diagnostics & Live Telemetry Monitor with JSON streaming API.
4. **Decoupled Architecture**: Feature 1 and Feature 2 are packaged with their own `standalone.py` microservice entry points, allowing them to effortlessly fit into a brand new server or run as isolated containers!

---

## 📁 Repository Structure

```
SmallApp/
├── app/
│   ├── __init__.py                # App factory with dynamic feature registration
│   ├── config.py                  # Environment config & feature toggles
│   ├── main/                      # Main Feature: Home Page Gateway
│   │   ├── __init__.py
│   │   └── routes.py              # Routes: /, /health, /api/info
│   ├── features/
│   │   ├── feature1/              # Feature 1 Module: Analytics Calculator
│   │   │   ├── __init__.py
│   │   │   ├── routes.py          # Routes: /feature1, /feature1/api/calculate
│   │   │   ├── standalone.py      # Standalone server runner for new server
│   │   │   └── templates/
│   │   └── feature2/              # Feature 2 Module: Diagnostics & Health
│   │       ├── __init__.py
│   │       ├── routes.py          # Routes: /feature2, /feature2/api/diagnostics
│   │       ├── standalone.py      # Standalone server runner for new server
│   │       └── templates/
│   ├── static/                    # Responsive CSS & styling
│   └── templates/                 # Base layout, Home, 404 & 500 error pages
├── deploy/
│   ├── ec2-userdata.sh            # Automated EC2 user-data provisioning script
│   ├── deploy-ec2.sh              # CI/CD deployment script for EC2
│   ├── smallapp.service           # systemd unit configuration
│   └── nginx.conf                 # Nginx reverse proxy configuration
├── tests/
│   ├── test_home.py               # Home page & health tests
│   ├── test_feature1.py           # Feature 1 calculation & standalone tests
│   ├── test_feature2.py           # Feature 2 diagnostics & standalone tests
│   └── test_modularity.py         # Feature toggling & decoupling tests
├── azure-pipelines.yml            # Full Azure DevOps CI/CD pipeline
├── Dockerfile                     # Multi-stage production container
├── docker-compose.yml             # Unified & standalone container configurations
├── requirements.txt               # Production Python dependencies
├── requirements-dev.txt           # Testing & build dependencies
├── pytest.ini                     # Pytest test execution config
├── TEST_PLAN.md                   # Comprehensive QA Test Plan
└── DEVOPS_GUIDE.md                # GitHub, Azure DevOps & AWS EC2 Guide
```

---

## ⚡ Quickstart: Local Setup

### 1. Install Dependencies
```bash
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Run the Unified Master Server (Home + Features)
```bash
python run.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser:
* **Home Page**: [http://localhost:5000/](http://localhost:5000/)
* **Feature 1**: [http://localhost:5000/feature1](http://localhost:5000/feature1)
* **Feature 2**: [http://localhost:5000/feature2](http://localhost:5000/feature2)
* **Health API**: [http://localhost:5000/health](http://localhost:5000/health)

---

## 🚀 Running Features on a "New Server" (Decoupled Mode)

### Running Feature 1 on an Independent Server:
```bash
python -m app.features.feature1.standalone --host 0.0.0.0 --port 5001
```
Now Feature 1 is running as its own standalone microservice at `http://localhost:5001/`!

### Running Feature 2 on an Independent Server:
```bash
python -m app.features.feature2.standalone --host 0.0.0.0 --port 5002
```
Now Feature 2 is running as its own standalone microservice at `http://localhost:5002/`!

---

## 🐳 Docker Deployment

### Build and Run with Docker:
```bash
docker build -t smallapp-server:latest .
docker run -d -p 5000:5000 --name smallapp smallapp-server:latest
```

### Run Multi-Container Simulation with Docker Compose:
```bash
docker compose up -d
```
This launches:
* Port 5000: Master Unified Server
* Port 5001: Feature 1 Standalone Microservice
* Port 5002: Feature 2 Standalone Microservice

---

## 🧪 Testing

Execute the automated test suite with coverage reporting:
```bash
pytest --cov=app tests/
```

Generate JUnit XML reports for Azure DevOps:
```bash
pytest --junitxml=test-results/junit.xml --cov=app --cov-report=xml:coverage.xml tests/
```

---

## 🔄 Git Branching & PR Architecture

The repository contains three organized branches:
* `main`: Production-ready branch containing merged code.
* `feature/feature-1`: Contains Feature 1 implementation and tests.
* `feature/feature-2`: Contains Feature 2 implementation and tests.

To push all branches to your GitHub account:
```bash
git remote add origin https://github.com/<your-username>/SmallApp.git
git push -u origin --all
```

For complete instructions on configuring GitHub with Azure DevOps, Azure Artifacts, and AWS EC2 deployments, see [DEVOPS_GUIDE.md](file:///c:/Users/INDIA/Desktop/Arshad/SmallApp/DEVOPS_GUIDE.md).
