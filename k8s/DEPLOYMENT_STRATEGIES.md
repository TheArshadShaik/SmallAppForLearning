# Kubernetes 0% Downtime Deployment Strategies

This guide details the engineering principles and implementation specifications for achieving **100% availability (zero dropped requests / 0% downtime)** during application updates in production.

---

## 1. Anatomy of 0% Downtime in Kubernetes

To achieve true zero-downtime, the application lifecycle and the Kubernetes networking layer must synchronize cleanly:

```
[Deploy Triggered]
       │
       ▼
1. Spin up New Pod ─────────► Passes Startup & Readiness Probes
                                         │
                                         ▼
2. Endpoint Controller ──────► Adds New Pod to Service Endpoints
                                         │
                                         ▼
3. Traffic Routes to New Pod  (Both old & new handle requests)
                                         │
                                         ▼
4. Kube-proxy removes Old Pod from iptables/IPVS (Takes 2-5 seconds)
                                         │
                                         ▼
5. Old Pod preStop Hook fires ─► "sleep 10" (Drains in-flight HTTP requests)
                                         │
                                         ▼
6. Gunicorn receives SIGTERM ─► Gracefully shuts down active workers
                                         │
                                         ▼
7. Old Pod Terminated ───────► Zero 502/504 errors experienced by users
```

### The 4 Core Prerequisites:
1. **`readinessProbe`**: Prevents user traffic from hitting new pods until Gunicorn is initialized.
2. **`maxUnavailable: 0`**: Prevents Kubernetes from terminating any active pod until a new pod is healthy.
3. **`preStop: sleep 10`**: Gives `kube-proxy` enough time to propagate iptables rules across all nodes before the pod stops accepting connections.
4. **`PodDisruptionBudget (PDB)`**: Guarantees a minimum number of pods remain alive during Kubernetes node upgrades, drains, or autoscaling events.

---

## 2. Comparison Matrix of Deployment Strategies

| Strategy | Risk Level | Resource Overhead | Cutover Speed | Rollback Speed | Automated Verification |
|---|---|---|---|---|---|
| **Rolling Update** | Low | +25% Temporary Pods | Incremental (1-3 min) | Fast (`kubectl rollout undo`) | Readiness probe based |
| **Blue-Green** | Very Low | +100% (Double capacity) | Instantaneous (<1ms) | Instantaneous (<1ms) | Pre-switchboard Preview URL |
| **Canary** | Minimal | +10% to +20% Pods | Progressive (Step-based) | Instantaneous (Auto-abort) | Metric analysis (Prometheus/5xx) |

---

## 3. Strategy 1: 0% Downtime Rolling Update

### How it Works:
Pods are upgraded sequentially. If you run 4 replicas with `maxSurge: 25%` and `maxUnavailable: 0`:
1. Kubernetes launches Pod 5 (new version).
2. Pod 5 runs its `startupProbe` and `readinessProbe`.
3. Once Pod 5 is healthy, Kubernetes sends `SIGTERM` to Pod 1.
4. Pod 1 executes `preStop: sleep 10` to drain connections, then shuts down.
5. Process repeats for Pods 2, 3, and 4.

### Manifest Configuration:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%
    maxUnavailable: 0
```

### Verification & Rollback:
```bash
# Check rollout status
kubectl rollout status deployment/smallapp-deployment -n smallapp

# View revision history
kubectl rollout history deployment/smallapp-deployment -n smallapp

# Instant rollback to previous revision
kubectl rollout undo deployment/smallapp-deployment -n smallapp
```

---

## 4. Strategy 2: Blue-Green Deployment

### How it Works:
* **Blue Fleet (Active):** Currently handles 100% of user traffic on `smallapp-production-service`.
* **Green Fleet (Preview):** Deployed with the new code release on `smallapp-preview-service`.
* **Verification:** Internal QA or automated smoke test suites validate the Green environment on the preview URL.
* **Cutover:** The service selector is updated to point to Green. All traffic switches instantly with zero downtime.

### Implementation with Argo Rollouts:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: smallapp-bluegreen-rollout
spec:
  strategy:
    blueGreen:
      activeService: smallapp-production-service
      previewService: smallapp-preview-service
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 60
```

### Operational Commands:
```bash
# Promote preview to active production
kubectl argo rollouts promote smallapp-bluegreen-rollout -n smallapp

# Abort rollout
kubectl argo rollouts abort smallapp-bluegreen-rollout -n smallapp
```

---

## 5. Strategy 3: Canary Progressive Delivery

### How it Works:
Canary deployment shifts traffic incrementally:
* **Step 1 (10%):** 10% of user traffic is routed to Canary pods. Metrics (HTTP 5xx error rate, latency) are analyzed for 5 minutes.
* **Step 2 (25%):** Traffic increases to 25%. Analyzed for 10 minutes.
* **Step 3 (50%):** Paused for human approval / QA confirmation.
* **Step 4 (100%):** Fully promoted to stable.

### Automated Metric Analysis (`AnalysisTemplate`):
If error rates exceed 1% at any point, Argo Rollouts **automatically rolls back** 100% of traffic to the stable version.

```yaml
analysis:
  templates:
    - templateName: success-rate-analysis
  args:
    - name: service-name
      value: smallapp-canary-service
```

### Manual Promotion or Abort:
```bash
# View live canary progress in terminal
kubectl argo rollouts get rollout smallapp-canary-rollout -n smallapp --watch

# Manually advance to next step
kubectl argo rollouts promote smallapp-canary-rollout -n smallapp

# Emergency abort (Instant return to stable)
kubectl argo rollouts abort smallapp-canary-rollout -n smallapp
```

---

## 6. High Availability Guardrails

### 1. PodDisruptionBudget (PDB)
Ensures at least 2 replicas remain accessible during node upgrades, cordon/drain operations, and autoscaling:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: smallapp-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: smallapp
```

### 2. Horizontal Pod Autoscaler (HPA)
Automatically scales pods between 3 and 10 based on CPU (70%) and Memory (80%) utilization.
