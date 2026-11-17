# Kubernetes Operations & Deployment Runbook

This guide covers local development, cloud provisioning, Helm management, and production operations for SmallApp on Kubernetes.

---

## 1. Quick Start: Local Cluster Testing

You can run SmallApp locally using **Minikube**, **Kind**, or **Docker Desktop (Kubernetes enabled)**.

### Option A: Using Minikube
```bash
# Start Minikube cluster
minikube start --cpus=2 --memory=4096

# Enable NGINX Ingress Controller
minikube addons enable ingress

# Enable Metrics Server (for HPA)
minikube addons enable metrics-server

# Deploy SmallApp using Helm
helm install smallapp ./k8s/application-k8s -n smallapp --create-namespace

# Access application
minikube tunnel
```

### Option B: Using Kind (Kubernetes in Docker)
```bash
# Create Kind cluster with Ingress port mappings
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
EOF

# Install NGINX Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Deploy SmallApp
kubectl apply -f k8s/manifests/
```

---

## 2. Helm Chart Management

### 1. Lint and Validate the Chart
```bash
helm lint ./k8s/application-k8s
```

### 2. Dry-Run / Template Output
```bash
# View generated YAML manifests
helm template smallapp ./k8s/application-k8s -f ./k8s/application-k8s/values-prod.yaml
```

### 3. Install or Upgrade Release
```bash
# Install / Upgrade in Production namespace
helm upgrade --install smallapp ./k8s/application-k8s \
  --namespace smallapp \
  --create-namespace \
  -f ./k8s/application-k8s/values.yaml \
  -f ./k8s/application-k8s/values-prod.yaml

# Upgrade image version only
helm upgrade smallapp ./k8s/application-k8s \
  --namespace smallapp \
  --set image.tag="1.0.2"
```

### 4. Rollback a Helm Release
```bash
# View release history
helm history smallapp -n smallapp

# Roll back to revision 1
helm rollback smallapp 1 -n smallapp
```

### 5. Run Chart Tests
```bash
helm test smallapp -n smallapp
```

---

## 3. Production Deployment on AWS EKS

### 1. Authenticate with AWS EKS
```bash
aws eks update-kubeconfig --region us-east-1 --name <YOUR_EKS_CLUSTER_NAME>
```

### 2. Install AWS Load Balancer Controller (for AWS ALB/NLB)
```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=<YOUR_EKS_CLUSTER_NAME> \
  --set serviceAccount.create=true
```

### 3. Deploy SmallApp Production
```bash
helm upgrade --install smallapp ./k8s/application-k8s \
  --namespace smallapp \
  --create-namespace \
  -f ./k8s/application-k8s/values-prod.yaml
```

---

## 4. Verification & Zero-Downtime Testing

### 1. Verify Pods, Service, and Ingress
```bash
kubectl get all -n smallapp
kubectl get ingress -n smallapp
kubectl get hpa -n smallapp
kubectl get pdb -n smallapp
```

### 2. Run Continuous Load Test During Deployment
To prove 0% downtime, open a terminal and run continuous HTTP requests while rolling out a new version:

```bash
# Run continuous requests (macOS/Linux)
while true; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health || echo "FAILED")
  echo "$(date +'%T') - HTTP Status: $STATUS"
  sleep 0.2
done
```

In another terminal, trigger an update:
```bash
kubectl set image deployment/smallapp-deployment smallapp=arshad200/smallapp:latest -n smallapp
```
**Expected Result:** Every single request returns `HTTP Status: 200`. Zero dropped packets, zero 502/503 errors.

---

## 5. Troubleshooting Cheat Sheet

| Issue | Diagnosis Command | Common Solution |
|---|---|---|
| `CrashLoopBackOff` | `kubectl logs <pod> -n smallapp --previous` | Check Gunicorn config, missing environment variables, or port binding. |
| `ImagePullBackOff` | `kubectl describe pod <pod> -n smallapp` | Verify Docker Hub repository name and tag; check imagePullSecrets. |
| `Pending` Pods | `kubectl describe pod <pod> -n smallapp` | Cluster CPU/Memory exhaustion or nodeSelector/toleration mismatch. |
| Readiness Failure | `kubectl describe pod <pod> -n smallapp` | App took too long to boot; increase `initialDelaySeconds` in `startupProbe`. |
| Ingress 502 Bad Gateway | `kubectl get endpoints smallapp-service -n smallapp` | Pods failing readiness check, so no endpoints are registered behind the Service. |
