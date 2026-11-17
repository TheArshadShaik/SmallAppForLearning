#!/bin/bash
# ==============================================================
# ArgoCD & Argo Rollouts Installation Script
# ==============================================================
set -euo pipefail

echo "=========================================================="
echo " Installing ArgoCD on Kubernetes Cluster..."
echo "=========================================================="

# 1. Create argocd namespace
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

# 2. Install official ArgoCD manifests
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 3. Install Argo Rollouts controller (for Blue-Green & Canary strategies)
echo "==> Installing Argo Rollouts Controller..."
kubectl create namespace argo-rollouts --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

echo "==> Waiting for ArgoCD server deployment to become available..."
kubectl wait --for=condition=Available deployment/argocd-server -n argocd --timeout=300s

echo "=========================================================="
echo " ArgoCD & Argo Rollouts Successfully Installed!"
echo "=========================================================="
echo ""
echo "Access the ArgoCD Web UI:"
echo "  kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "  URL: https://localhost:8080"
echo "  User: admin"
echo "  Initial Password:"
echo "    kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d && echo"
echo ""
