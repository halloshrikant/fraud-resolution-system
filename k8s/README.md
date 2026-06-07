# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Fraud Resolution System.

## Environments

- **Local Development**: Minikube (cost-free testing)
- **AWS Production**: EKS (production workloads)

## Directory Structure

```
k8s/
├── base/              # Common resources shared across environments
│   ├── namespace.yaml
│   ├── configmap.yaml
│   └── secrets.yaml
├── minikube/          # Local development overlay
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── redis-deployment.yaml
│   └── kustomization.yaml
└── eks/               # AWS production overlay
    ├── backend-deployment.yaml
    ├── frontend-deployment.yaml
    ├── redis-deployment.yaml
    ├── ingress.yaml
    └── kustomization.yaml
```

## Quick Start

### Minikube (Local)

```bash
# Start minikube
minikube start --cpus=4 --memory=8192

# Deploy to minikube
kubectl apply -k k8s/minikube

# Port forward to access locally
kubectl port-forward -n fraud-system svc/backend 8000:8000
kubectl port-forward -n fraud-system svc/frontend 5173:80

# Access the application
open http://localhost:5173
open http://localhost:8000/docs
```

### EKS (AWS)

```bash
# Configure AWS credentials
aws configure

# Create EKS cluster (one-time setup)
eksctl create cluster \
  --name fraud-resolution-prod \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 4

# Deploy to EKS
kubectl apply -k k8s/eks

# Get load balancer URL
kubectl get ingress -n fraud-system
```

## Configuration

### Environment Variables

Edit `k8s/base/configmap.yaml` for non-sensitive config:
- REDIS_HOST
- AWS_REGION
- MLFLOW_TRACKING_URI

Edit `k8s/base/secrets.yaml` for sensitive data:
- COGNITO_USER_POOL_ID
- COGNITO_CLIENT_ID
- AWS credentials

### Resource Limits

**Minikube** (minimal resources):
- Backend: 256Mi RAM, 0.5 CPU
- Frontend: 128Mi RAM, 0.25 CPU
- Redis: 512Mi RAM, 0.5 CPU

**EKS** (production):
- Backend: 1Gi RAM, 1 CPU (auto-scaling 2-10 replicas)
- Frontend: 256Mi RAM, 0.5 CPU (auto-scaling 2-5 replicas)
- Redis: 2Gi RAM, 1 CPU (persistent volume)

## Monitoring

```bash
# Check pod status
kubectl get pods -n fraud-system

# View logs
kubectl logs -f -n fraud-system deployment/backend
kubectl logs -f -n fraud-system deployment/frontend

# Check resource usage
kubectl top pods -n fraud-system
```

## Cost Optimization

**For testing**: Use minikube (free)
**For production**: 
1. Use EKS with spot instances
2. Enable cluster autoscaler
3. Set pod disruption budgets
4. Use AWS cost allocation tags

```bash
# Switch from EKS to minikube to save costs
kubectl config use-context minikube
```
