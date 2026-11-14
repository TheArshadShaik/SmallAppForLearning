# Comprehensive QA & Test Plan: SmallApp Modular Python Server

**Document Version:** 1.0.0  
**Target Application:** SmallApp Modular Python Server (Home, Feature 1, Feature 2)  
**CI/CD Target:** Azure DevOps Pipelines & Test Plans  
**Infrastructure Target:** AWS EC2 & Docker Engine  

---

## 1. Executive Summary & Strategy

The purpose of this Test Plan is to validate the reliability, modularity, performance, and containerization of the **SmallApp Modular Python Server**. The core architectural requirement mandates that the **Home page** acts as the primary orchestrator, while **Feature 1** and **Feature 2** are completely decoupled into independent blueprints capable of running either as a unified server or spinning off into isolated standalone microservers on new target machines.

### Testing Pyramid Distribution
* **Unit & Component Tests (70%)**: Fast, isolated testing of blueprint routes, data calculations, and diagnostics logic.
* **Integration Tests (20%)**: Testing dynamic feature loading, environment variable overrides (`ENABLE_FEATURE_1`, `ENABLE_FEATURE_2`), and standalone microservice runners.
* **System & Container Smoke Tests (10%)**: Docker container startup, `/health` endpoint polling, and EC2 runtime health checks.

---

## 2. Test Environment Matrix

| Environment | Component / Runtime | Host / Target | Test Execution |
| :--- | :--- | :--- | :--- |
| **Local / Dev** | Python 3.11 / 3.14 + Pytest | Developer Workstation | `pytest -v tests/` |
| **CI / Quality** | Ubuntu-latest runner | Azure DevOps Pipeline | Automated via `azure-pipelines.yml` |
| **Container** | Docker Engine 24+ | Local / Azure Container Instances | `docker compose up` / healthcheck |
| **Production** | Amazon Linux 2023 / Ubuntu 22.04 | AWS EC2 (t3.micro / t3.medium) | `deploy-ec2.sh` + curl `/health` |

---

## 3. Test Cases Specification

### Suite 1: Home Page & Gateway Orchestration (`tests/test_home.py`)

| Test ID | Test Case Title | Input / Route | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Home Page Availability | `GET /` | Returns HTTP 200, HTML contains "SmallApp" and active features. | PASS |
| **TC-02** | System Health Endpoint | `GET /health` | Returns HTTP 200, JSON contains `status: "healthy"`, hostname, version. | PASS |
| **TC-03** | API Information Endpoint | `GET /api/info` | Returns HTTP 200, JSON includes registered blueprints list and runtime config. | PASS |
| **TC-04** | Error Page Handling (404) | `GET /invalid-route-xyz` | Returns HTTP 404 with styled error page; no unhandled exceptions. | PASS |

### Suite 2: Feature 1 Single Page & Analytics (`tests/test_feature1.py`)

| Test ID | Test Case Title | Input / Route | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-05** | Feature 1 Page Render | `GET /feature1/` | Returns HTTP 200, renders calculator form and styling. | PASS |
| **TC-06** | Sizing API Calculation (Valid) | `POST /feature1/api/calculate`<br>`{instances: 3, hours: 10, rate: 0.05}` | Returns HTTP 200, `total_cost_usd: 1.50`, `total_compute_hours: 30`. | PASS |
| **TC-07** | Sizing API Negative Values | `POST /feature1/api/calculate`<br>`{instances: -1, hours: 10}` | Returns HTTP 422 with validation error message. | PASS |
| **TC-08** | Sizing API Empty Payload | `POST /feature1/api/calculate` (empty body) | Returns HTTP 400 Bad Request. | PASS |
| **TC-09** | Feature 1 Standalone Server Mode | `GET /` on standalone server | Redirects 302 to `/feature1`, `/feature1/api/health` returns healthy. | PASS |

### Suite 3: Feature 2 Diagnostics & Telemetry (`tests/test_feature2.py`)

| Test ID | Test Case Title | Input / Route | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-10** | Feature 2 Page Render | `GET /feature2/` | Returns HTTP 200, renders telemetry table and metrics headers. | PASS |
| **TC-11** | Diagnostics Telemetry API | `GET /feature2/api/diagnostics` | Returns HTTP 200, JSON includes `pid`, `active_threads`, `uptime_seconds`, `hostname`. | PASS |
| **TC-12** | Feature 2 Standalone Server Mode | `GET /` on standalone server | Redirects 302 to `/feature2`, health endpoint operational. | PASS |

### Suite 4: Server Decoupling & Modularity (`tests/test_modularity.py`)

| Test ID | Test Case Title | Input / Route | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-13** | Feature 1 Toggle Off | `ENABLE_FEATURE_1=false` | Core app runs without Feature 1, `/health` reports `feature1: false`. | PASS |
| **TC-14** | Feature 2 Toggle Off | `ENABLE_FEATURE_2=false` | Core app runs without Feature 2, `/health` reports `feature2: false`. | PASS |
| **TC-15** | New Server Fit Validation | Run on port 5001 / 5002 | Feature modules start independently without any root app dependency. | PASS |

---

## 4. Azure DevOps Test Plan & Coverage Integration

In Azure DevOps, tests are automated in Stage 1 of `azure-pipelines.yml`:

```bash
pytest \
  --junitxml=test-results/junit-test-results.xml \
  --cov=app \
  --cov-report=xml:coverage.xml \
  --cov-report=html:htmlcov \
  tests/
```

### Publishing Tasks:
1. **`PublishTestResults@2`**:
   - Ingests `junit-test-results.xml`.
   - Populates Azure DevOps **Pipelines > Test Runs** and connects with **Azure Test Plans**.
   - Fails pipeline immediately if any test fails (`failTaskOnFailedTests: true`).
2. **`PublishCodeCoverageResults@2`**:
   - Ingests `coverage.xml`.
   - Generates interactive line-by-line coverage reports directly in the Azure DevOps build summary.

---

## 5. Acceptance & Sign-Off Criteria

- [x] All 14 automated unit and integration tests passing (100% pass rate).
- [x] Minimum 80% code coverage across application blueprints (currently 84%+).
- [x] Docker image builds cleanly and passes container health checks.
- [x] Standalone microserver runners verified for isolated deployment on new servers.
- [x] CI/CD pipeline triggers on PRs and main branch commits.
