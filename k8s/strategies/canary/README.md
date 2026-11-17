# Canary Deployment Strategy (0% Downtime & Risk Mitigation)

## Overview
A **Canary Deployment** progressively introduces a new software release to a small fraction of users (e.g. 10%) before rolling it out to 100% of the fleet.

If any anomalies, error spikes (HTTP 5xx), or latency degradations occur, the canary is **automatically aborted**, rolling back 100% of traffic to the stable version with zero impact on the majority of users.

```
                    +-----------------------+
                    |   Ingress / Router    |
                    +-----------+-----------+
                                |
             +------------------+------------------+
             | (90% Traffic)                       | (10% Traffic)
             v                                     v
     +---------------+                     +---------------+
     | Stable Fleet  |                     | Canary Fleet  |
     |   (v1.0.0)    |                     |   (v1.0.1)    |
     +---------------+                     +---------------+
```

---

## Method 1: Using Argo Rollouts (Progressive Delivery)

### 1. Apply Canary Rollout & Analysis Template
```bash
kubectl apply -f analysis-template.yaml
kubectl apply -f rollout-canary.yaml
```

### 2. Trigger New Canary Release
```bash
kubectl argo rollouts set image smallapp-canary-rollout web=arshad200/smallapp:1.0.2 -n smallapp
```

### 3. Progressive Steps Flow
* **Step 1:** Sends 10% traffic to Canary. Runs automated metric analysis for 5 minutes.
* **Step 2:** Promotes to 25% traffic. Runs automated analysis for 10 minutes.
* **Step 3:** Promotes to 50% traffic. Pauses for human confirmation.
* **Step 4:** Promotes to 100% full production traffic.

### 4. Manually Promote or Abort
```bash
# Approve advancement to next step
kubectl argo rollouts promote smallapp-canary-rollout -n smallapp

# Abort and instantly roll back to stable
kubectl argo rollouts abort smallapp-canary-rollout -n smallapp
```

---

## Method 2: Native NGINX Ingress Canary (No Extra Controller)

### 1. Deploy Stable & Canary Pods
Deploy two deployments: `smallapp-stable` and `smallapp-canary`.

### 2. Apply Canary Ingress
```bash
kubectl apply -f ingress-canary.yaml
```

### 3. Test Header-Based Routing (QA Validation)
Send requests with the `X-Canary-Test: always` header:
```bash
curl -H "X-Canary-Test: always" http://smallapp.local/
```
*This request will bypass the 10% weight and route 100% directly to the Canary pods for immediate validation!*

### 4. Increase Weight Progressively
To increase traffic to 50%:
```bash
kubectl annotate ingress smallapp-canary-ingress -n smallapp \
  nginx.ingress.kubernetes.io/canary-weight="50" --overwrite
```

### 5. Instant Rollback
```bash
kubectl delete ingress smallapp-canary-ingress -n smallapp
```
*(All traffic immediately routes back to 100% stable).*
