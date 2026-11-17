# 0% Downtime Rolling Update Strategy

## Overview
A **Rolling Update** replaces old pods with new pods incrementally, one by one or in small batches, ensuring continuous application availability without downtime.

## How 0% Downtime is Guaranteed
Four interconnected Kubernetes mechanisms guarantee zero dropped connections:

1. **`maxUnavailable: 0`**:
   Kubernetes will **never** shut down an existing pod until a replacement pod is fully running, initialized, and passing all readiness checks.
2. **`maxSurge: 25%` (or 1+)**:
   Kubernetes creates new pods alongside existing pods (e.g. 4 existing pods + 1 new pod = 5 total pods during rollout).
3. **`readinessProbe`**:
   The `/health` endpoint is continuously probed. Traffic is only directed to new pods once HTTP 200 is verified.
4. **`preStop` Lifecycle Hook (`sleep 10`)**:
   When an old pod is marked for termination:
   - Kube-proxy removes the pod from iptables / IPVS service endpoints.
   - The `preStop` hook waits 10 seconds to allow in-flight HTTP requests to complete cleanly before Gunicorn receives `SIGTERM`.

## Operational Commands

### 1. Apply Deployment
```bash
kubectl apply -f rolling-update.yaml
```

### 2. Update Image (Triggers Rolling Update)
```bash
kubectl set image deployment/smallapp-rolling-update web=arshad200/smallapp:1.0.2 -n smallapp
```

### 3. Monitor Rollout in Real-Time
```bash
kubectl rollout status deployment/smallapp-rolling-update -n smallapp
```

### 4. Inspect Revision History
```bash
kubectl rollout history deployment/smallapp-rolling-update -n smallapp
```

### 5. Instant Rollback (Zero Downtime Undo)
```bash
kubectl rollout undo deployment/smallapp-rolling-update -n smallapp
```
