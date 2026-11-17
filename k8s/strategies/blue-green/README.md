# Blue-Green Deployment Strategy (0% Downtime)

## Overview
**Blue-Green Deployment** maintains two identical production environments:
* **Blue Environment**: Currently receives 100% of live user traffic.
* **Green Environment**: New release version deployed alongside Blue.

Once Green passes all automated smoke tests, internal QA, and validation via the `preview` service, traffic is **instantly switched** from Blue to Green at the service/load-balancer level with 0 downtime.

```
       +-----------------------+
       |   Ingress / Router    |
       +-----------+-----------+
                   |
     [Instant Selector Switch: 0ms Downtime]
                   |
         +---------+---------+
         |                   |
         v                   v
   +-----------+       +-----------+
   |   BLUE    |       |   GREEN   |
   | (Active)  |       | (Preview) |
   |  v1.0.0   |       |  v1.0.1   |
   +-----------+       +-----------+
```

---

## Method 1: Using Argo Rollouts (Automated Controller)

### 1. Apply Services and Rollout
```bash
kubectl apply -f service-active.yaml
kubectl apply -f service-preview.yaml
kubectl apply -f rollout-bluegreen.yaml
```

### 2. Trigger New Release
Update the rollout image:
```bash
kubectl argo rollouts set image smallapp-bluegreen-rollout web=arshad200/smallapp:1.0.1 -n smallapp
```

### 3. Verify Preview Environment
Green pods spin up and are connected to `smallapp-preview-service`. Test them independently:
```bash
kubectl port-forward svc/smallapp-preview-service 8080:80 -n smallapp
curl http://localhost:8080/health
curl http://localhost:8080/feature1
```

### 4. Promote Green to Production (Instant Cutover)
```bash
kubectl argo rollouts promote smallapp-bluegreen-rollout -n smallapp
```
*Live traffic switches to Green in under 1 millisecond with zero dropped packets.*

### 5. Instant Rollback (If Needed)
```bash
kubectl argo rollouts abort smallapp-bluegreen-rollout -n smallapp
kubectl argo rollouts undo smallapp-bluegreen-rollout -n smallapp
```

---

## Method 2: Native Kubernetes (Without Argo Rollouts)

If Argo Rollouts CRD is not installed, achieve Blue-Green using native Kubernetes service selector manipulation:

### 1. Deploy Blue and Green
```bash
kubectl apply -f native-bluegreen.yaml
kubectl apply -f service-active.yaml
```

### 2. Verify Green Pods are Ready
```bash
kubectl get pods -n smallapp -l version=green
```

### 3. Switch Live Traffic to Green Instantly
```bash
kubectl patch service smallapp-production-service -n smallapp -p '{"spec":{"selector":{"version":"green"}}}'
```

### 4. Rollback Instantly to Blue
```bash
kubectl patch service smallapp-production-service -n smallapp -p '{"spec":{"selector":{"version":"blue"}}}'
```
