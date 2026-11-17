# SmallApp Kubernetes Architecture & GitOps Suite

This directory contains the production-grade Kubernetes manifests, Helm charts, ArgoCD GitOps pipelines, and 0% downtime deployment strategies for SmallApp.

---

## Directory Structure

```text
k8s/
├── README.md                      # Architecture Overview (This file)
├── K8S_GUIDE.md                   # Complete Kubernetes Runbook (Minikube, EKS, Helm)
├── DEPLOYMENT_STRATEGIES.md       # Zero-Downtime Deep Dive (Rolling, Blue-Green, Canary)
├── ARGOCD_SETUP.md                # GitOps Pipeline & Self-Healing Setup with ArgoCD
│
├── manifests/                     # Declarative Raw Kubernetes Manifests
│   ├── namespace.yaml             # Dedicated 'smallapp' namespace
│   ├── configmap.yaml             # Application configuration & feature flags
│   ├── secret.yaml                # Production secrets & database credentials
│   ├── deployment.yaml            # 0% downtime rolling update deployment
│   ├── service.yaml               # ClusterIP internal service
│   ├── ingress.yaml               # NGINX Ingress rules
│   ├── hpa.yaml                   # Horizontal Pod Autoscaler (CPU 70%, Memory 80%)
│   ├── pdb.yaml                   # PodDisruptionBudget (minAvailable: 2)
│   └── networkpolicy.yaml         # Ingress/Egress zero-trust network policy
│
├── application-k8s/               # Production Helm 3 Chart
│   ├── Chart.yaml                 # Chart metadata
│   ├── values.yaml                # Base default configuration
│   ├── values-dev.yaml            # Development environment overrides
│   ├── values-prod.yaml           # High-availability production overrides
│   └── templates/                 # Parameterized Jinja/Go templates
│       ├── _helpers.tpl
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       ├── configmap.yaml
│       ├── secret.yaml
│       ├── serviceaccount.yaml
│       ├── hpa.yaml
│       ├── pdb.yaml
│       └── tests/
│           └── test-connection.yaml
│
├── strategies/                    # 0% Downtime Deployment Strategy Implementations
│   ├── rolling-update/            # Native K8s maxSurge=25%, maxUnavailable=0 + preStop
│   ├── blue-green/                # Argo Rollouts & Native Service-Switch Blue-Green
│   └── canary/                    # Argo Rollouts Progressive Delivery + Prometheus Analysis
│
└── argocd/                        # GitOps Architecture with ArgoCD
    ├── install-argocd.sh          # One-click ArgoCD & Argo Rollouts installer
    ├── project.yaml               # ArgoCD AppProject RBAC boundaries
    ├── application-dev.yaml       # Dev environment auto-sync application
    ├── application-prod.yaml      # Production environment self-healing application
    └── applicationset.yaml        # Multi-environment generator (Dev/Staging/Prod)
```

---

## Quick Navigation

| What do you want to do? | Guide / Path |
|---|---|
| **Deploy with raw YAMLs** | See [`manifests/`](manifests/) or run `kubectl apply -f k8s/manifests/` |
| **Deploy with Helm Chart** | See [`application-k8s/`](application-k8s/) or read [K8S_GUIDE.md](K8S_GUIDE.md) |
| **Set up GitOps with ArgoCD** | Read [ARGOCD_SETUP.md](ARGOCD_SETUP.md) & check [`argocd/`](argocd/) |
| **Implement Canary or Blue-Green** | Read [DEPLOYMENT_STRATEGIES.md](DEPLOYMENT_STRATEGIES.md) & check [`strategies/`](strategies/) |
| **Verify 0% Downtime** | Follow the Load Testing section in [K8S_GUIDE.md](K8S_GUIDE.md) |
