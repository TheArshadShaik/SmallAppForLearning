# ArgoCD GitOps Production Setup Guide

This guide details how to implement **GitOps** for SmallApp using **ArgoCD**, ensuring that your Kubernetes cluster state is continuously declared in Git, self-healing, and automatically deployed.

---

## 1. What is GitOps?

With GitOps:
* **Git is the Single Source of Truth:** All Kubernetes manifests, Helm charts, and environment overrides live in this repository.
* **Pull-Based Deployment:** Instead of GitHub Actions pushing directly into the Kubernetes cluster (which requires exposing cluster APIs and storing credentials in CI), **ArgoCD runs inside your cluster and pulls changes from Git**.
* **Automatic Drift Detection & Self-Healing:** If someone manually deletes a pod or modifies a service in the cluster, ArgoCD automatically overrides the drift and restores the declared Git state.

---

## 2. Step 1: Install ArgoCD & Argo Rollouts

Run the provided installation script or execute directly:

```bash
# 1. Create argocd namespace
kubectl create namespace argocd

# 2. Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 3. Install Argo Rollouts (for Blue-Green & Canary strategies)
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# 4. Wait for controller availability
kubectl wait --for=condition=Available deployment/argocd-server -n argocd --timeout=300s
```

---

## 3. Step 2: Access the ArgoCD Web UI

1. **Port-forward the ArgoCD UI:**
   ```bash
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   ```
2. Open your browser at: **`https://localhost:8080`**
3. **Login Credentials:**
   * **Username:** `admin`
   * **Password:** Retrieve the auto-generated password:
     ```bash
     kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
     ```

---

## 4. Step 3: Connect Your Git Repository

### For Public Repository:
No authentication needed. ArgoCD reads directly from `https://github.com/TheArshadShaik/SmallAppForLearning.git`.

### For Private Repository (via CLI):
```bash
argocd repo add https://github.com/TheArshadShaik/SmallAppForLearning.git \
  --username <YOUR_GITHUB_USERNAME> \
  --password <YOUR_PERSONAL_ACCESS_TOKEN>
```

---

## 5. Step 4: Deploy SmallApp Applications

### 1. Apply the Project RBAC & Boundaries:
```bash
kubectl apply -f k8s/argocd/project.yaml
```

### 2. Deploy Development Environment:
```bash
kubectl apply -f k8s/argocd/application-dev.yaml
```

### 3. Deploy Production Environment (With Auto-Sync & Self-Healing):
```bash
kubectl apply -f k8s/argocd/application-prod.yaml
```

---

## 6. How ArgoCD Automated Sync Works

The `application-prod.yaml` manifest defines:
```yaml
syncPolicy:
  automated:
    prune: true     # Deletes resources removed from Git
    selfHeal: true  # Reverts manual changes made in cluster
  syncOptions:
    - CreateNamespace=true
    - ApplyOutOfSyncOnly=true
```

### The Continuous Delivery Workflow:
1. Developer pushes a new commit or merges a PR into `main`.
2. GitHub Actions builds and pushes the new Docker image (`arshad200/smallapp:1.0.3`).
3. GitHub Actions (or developer) updates `image.tag` in `k8s/application-k8s/values.yaml` (or `values-prod.yaml`).
4. **ArgoCD automatically detects the commit**, synchronizes the cluster, and triggers a 0% downtime rolling update.

---

## 7. Multi-Environment ApplicationSet

To manage Dev, Staging, and Production from a single declarative manifest, apply the **ApplicationSet**:

```bash
kubectl apply -f k8s/argocd/applicationset.yaml
```

ArgoCD will automatically create three synchronized applications:
* `smallapp-dev` (namespace: `smallapp-dev`)
* `smallapp-staging` (namespace: `smallapp-staging`)
* `smallapp-prod` (namespace: `smallapp`)

---

## 8. ArgoCD CLI Quick Reference

```bash
# Log in to ArgoCD CLI
argocd login localhost:8080 --username admin --password <PASSWORD> --insecure

# List applications
argocd app list

# View sync status
argocd app get smallapp-production

# Trigger manual synchronization
argocd app sync smallapp-production

# View live deployment diff between Git and Cluster
argocd app diff smallapp-production

# Roll back application
argocd app rollback smallapp-production
```
