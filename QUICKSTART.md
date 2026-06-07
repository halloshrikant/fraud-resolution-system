# Quick Start Guide - Fraud Resolution System

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Minikube Deployment](#minikube-deployment)
3. [EKS Deployment](#eks-deployment)
4. [Testing](#testing)
5. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites
- Python 3.12+
- Redis Stack
- AWS Account (for Bedrock access)
- Node.js 18+ (for frontend)

### Step 1: Clone and Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install uv package manager (faster than pip)
pip install uv

# Install backend dependencies
uv pip install -e ".[dev]"

# Install agent packages
cd ../agents
uv pip install -e .

# Install ingestion pipeline
cd ../ingestion
uv pip install -e .
```

### Step 2: Configure Environment

```bash
cd ../backend

# Copy example configuration
cp .env.example .env

# Edit .env with your settings
nano .env  # or vim, code, etc.
```

**Minimum required configuration:**
```bash
DEV_MODE=True
REDIS_HOST=localhost
REDIS_TLS_PORT=6379
AWS_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_XXXXXXX  # Get from AWS Console
COGNITO_CLIENT_ID=xxxxxxxxxx            # Get from AWS Console
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
ALLOWED_ORIGINS=["http://localhost:5173"]
```

### Step 3: Start Redis

**Option 1: Docker (Recommended)**
```bash
docker run -d -p 6379:6379 --name fraud-redis redis/redis-stack:latest
```

**Option 2: Local Installation**
```bash
# Ubuntu/Debian
sudo apt install redis-stack-server
redis-stack-server

# macOS
brew tap redis-stack/redis-stack
brew install redis-stack
redis-stack-server
```

### Step 4: Start Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
✓ Redis connection established
INFO:     Application startup complete.
```

### Step 5: Verify Installation

```bash
# Check API is running
curl http://localhost:8000/

# Should return:
# {
#   "name": "Fraud Resolution API",
#   "version": "1.0.0",
#   "status": "operational",
#   "mode": "development",
#   ...
# }

# Access interactive API docs
open http://localhost:8000/docs
```

### Step 6: Test with Sample Dispute

```bash
curl -X POST http://localhost:8000/api/v1/dispute \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "dev-customer-123",
    "transaction_id": "txn-test-001",
    "dispute_amount_usd": 149.99,
    "dispute_reason": "I did not authorize this charge. It appears fraudulent."
  }'

# Should return:
# {
#   "case_id": "uuid-here",
#   "status": "PENDING",
#   "message": "Dispute submitted. Processing initiated."
# }
```

---

## Minikube Deployment

### Prerequisites
- Minikube installed
- kubectl installed
- Docker installed

### Quick Deploy

```bash
# Use the deployment script
./deploy.sh minikube

# Or manually:
minikube start --cpus=4 --memory=8192
kubectl apply -k k8s/minikube

# Port forward to access locally
kubectl port-forward -n fraud-system svc/backend 8000:8000
```

### Access Services

```bash
# Get minikube service URL
minikube service backend -n fraud-system --url

# Or use port forwarding
kubectl port-forward -n fraud-system svc/backend 8000:8000

# Access API
curl http://localhost:8000/
```

### View Logs

```bash
# Backend logs
kubectl logs -f -n fraud-system deployment/backend

# Redis logs
kubectl logs -f -n fraud-system deployment/redis

# All pods status
kubectl get pods -n fraud-system
```

---

## EKS Deployment

### Prerequisites
- AWS CLI configured
- eksctl installed
- kubectl installed

### Step 1: Create EKS Cluster (One-time)

```bash
eksctl create cluster \
  --name fraud-resolution-prod \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 4 \
  --managed
```

This takes ~15 minutes.

### Step 2: Configure kubectl

```bash
# Update kubeconfig
aws eks update-kubeconfig --name fraud-resolution-prod --region us-east-1

# Verify connection
kubectl get nodes
```

### Step 3: Deploy Application

```bash
# Use deployment script
./deploy.sh eks

# Or manually:
# 1. Create ECR repository
aws ecr create-repository --repository-name fraud-resolution-backend

# 2. Login to ECR
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# 3. Build and push image
docker build -t fraud-resolution-backend:latest ./backend
docker tag fraud-resolution-backend:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/fraud-resolution-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/fraud-resolution-backend:latest

# 4. Deploy to EKS
kubectl apply -k k8s/eks
```

### Step 4: Get Load Balancer URL

```bash
# Wait for load balancer to be created
kubectl get svc -n fraud-system backend -w

# Get URL
LB_URL=$(kubectl get svc backend -n fraud-system -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "API URL: http://$LB_URL:8000"
```

### Step 5: Test Production Deployment

```bash
# Health check
curl http://$LB_URL:8000/health

# API info (docs disabled in production)
curl http://$LB_URL:8000/
```

---

## Testing

### Run Agent Test Suite

```bash
cd /home/ubuntu
source backend/.venv/bin/activate
python test_agents.py
```

**Expected output:**
```
================================================================================
FRAUD RESOLUTION SYSTEM - AGENT TEST SUITE
================================================================================

[TEST 1] Importing agent modules...
✓ All shared modules imported successfully
✓ Orchestrator agent imported
✓ RAG agent imported
✓ Transaction analyst agent imported
✓ Fraud investigator agent imported

[TEST 2] Testing ingestion pipeline modules...
✓ Ingestion pipeline modules imported

...

✅ ALL TESTS PASSED - System is operational
```

### Frontend Testing

```bash
cd frontend
npm install
npm run dev

# Access at http://localhost:5173
```

---

## Troubleshooting

### Issue: "Address already in use" on port 8000

**Solution:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or kill all uvicorn processes
pkill -f uvicorn
```

### Issue: Redis connection failed

**Solution:**
```bash
# Check if Redis is running
docker ps | grep redis

# Start Redis if not running
docker run -d -p 6379:6379 --name fraud-redis redis/redis-stack:latest

# Test connection
redis-cli ping  # Should return PONG
```

### Issue: Import errors for agents

**Solution:**
```bash
cd backend && source .venv/bin/activate
cd ../agents && uv pip install -e .
cd ../ingestion && uv pip install -e .
cd ../backend
```

### Issue: 404 Not Found on root URL

**Solution:**
- Make sure server reloaded after changes
- Check that DEV_MODE=True in .env
- Verify you're accessing http://localhost:8000/ (with trailing slash)

### Issue: Minikube won't start

**Solution:**
```bash
# Delete existing cluster
minikube delete

# Start fresh
minikube start --cpus=4 --memory=8192 --driver=docker

# If driver issues, try different driver
minikube start --driver=virtualbox
```

### Issue: EKS deployment fails

**Solution:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify kubectl context
kubectl config current-context

# Check pod status
kubectl get pods -n fraud-system

# View pod logs for errors
kubectl logs -n fraud-system <pod-name>
```

### Issue: Agent tests fail

**Solution:**
```bash
# Reinstall all packages
cd backend && source .venv/bin/activate
uv pip install -e ".[dev]"
cd ../agents && uv pip install -e .
cd ../ingestion && uv pip install -e .

# Verify openai-agents SDK installed
pip show openai-agents
```

---

## Cost Optimization

**Development workflow to minimize AWS costs:**

1. **Develop locally** (free)
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Test in minikube** (free)
   ```bash
   ./deploy.sh minikube
   ```

3. **Deploy to EKS for final testing** (paid)
   ```bash
   ./deploy.sh eks
   # Test thoroughly
   ```

4. **Delete EKS cluster when not in use**
   ```bash
   eksctl delete cluster --name fraud-resolution-prod --region us-east-1
   ```

5. **Recreate when needed**
   ```bash
   eksctl create cluster --config-file k8s/eks-config.yaml
   ```

**Estimated costs:**
- Local dev: $0
- Minikube: $0
- EKS (t3.medium × 3 nodes): ~$75/month
- Bedrock pay-per-use: ~$0.01 per dispute

---

## Next Steps

1. ✅ Local development working
2. ✅ Minikube deployment configured
3. ✅ EKS manifests created
4. 🔲 Implement real agent logic (replace mocks)
5. 🔲 Set up CI/CD pipeline
6. 🔲 Configure AWS Bedrock models
7. 🔲 Run data ingestion pipeline
8. 🔲 Set up monitoring and alerting

---

## Support

For questions or issues:
- Check [README.md](README.md)
- View [k8s/README.md](k8s/README.md)
- Review [SYSTEM_STATUS.md](SYSTEM_STATUS.md)
