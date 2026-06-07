# Fraud Resolution System 🛡️

AI-powered fraud dispute resolution system using multi-agent orchestration with AWS Bedrock.

## Overview

This system processes credit card dispute claims using specialized AI agents:
- **RAG Policy Agent**: Retrieves relevant bank policies from vector database
- **Transaction Analyst**: Analyzes transaction history and patterns  
- **Fraud Investigator**: Assesses fraud risk and evidence
- **Orchestrator**: Coordinates agents and makes final resolution decision

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Customer  │─────▶│   Backend    │─────▶│   Agents    │
│   Portal    │◀─────│   FastAPI    │◀─────│  (Bedrock)  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                       │
                            ▼                       ▼
                     ┌──────────────┐      ┌─────────────┐
                     │    Redis     │      │   MLflow    │
                     │  (Sessions)  │      │  (Tracking) │
                     └──────────────┘      └─────────────┘
```

**Tech Stack:**
- **Backend**: FastAPI + Python 3.12
- **Frontend**: React + TypeScript + Vite
- **Database**: Redis Stack (JSON + Vector Search)
- **AI/ML**: AWS Bedrock (Nova Lite, Claude) via LiteLLM
- **Embeddings**: Amazon Titan Embed Text v2 (1536 dims)
- **Auth**: AWS Cognito JWT
- **Observability**: MLflow + Structured Logging
- **Deployment**: Kubernetes (Minikube local, EKS production)

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Redis Stack
- AWS Account (for Bedrock)
- Docker (optional)
- Minikube (for local k8s)

### Local Development Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd fraud-resolution-system

# 2. Backend setup
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install uv
uv pip install -e ".[dev]"

# 3. Install agent packages
cd ../agents
uv pip install -e .

cd ../ingestion
uv pip install -e .

# 4. Configure environment
cd ../backend
cp .env.example .env
# Edit .env with your AWS credentials and settings

# 5. Start Redis
docker run -d -p 6379:6379 redis/redis-stack:latest

# 6. Start backend
uvicorn app.main:app --reload --port 8000

# 7. Frontend setup (new terminal)
cd ../frontend
npm install
npm run dev
```

Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Kubernetes Deployment

See [k8s/README.md](k8s/README.md) for detailed Kubernetes deployment instructions.

**Quick deploy to Minikube:**
```bash
minikube start --cpus=4 --memory=8192
kubectl apply -k k8s/minikube
kubectl port-forward -n fraud-system svc/backend 8000:8000
```

**Deploy to EKS:**
```bash
# One-time EKS cluster creation
eksctl create cluster --name fraud-prod --region us-east-1 --nodes 3

# Deploy application
kubectl apply -k k8s/eks

# Get load balancer URL
kubectl get svc -n fraud-system backend
```

## Project Structure

```
fraud-resolution-system/
├── backend/              # FastAPI REST API
│   ├── app/
│   │   ├── api/v1/      # API endpoints
│   │   ├── middleware/  # Auth, logging, rate limiting
│   │   ├── models/      # Pydantic data models
│   │   └── services/    # Business logic (Redis, orchestrator)
│   ├── pyproject.toml   # Python dependencies
│   └── .env             # Environment config
│
├── frontend/            # React TypeScript SPA
│   ├── src/
│   │   ├── portals/    # Customer & Analyst views
│   │   ├── api/        # API client
│   │   ├── hooks/      # React hooks
│   │   └── types/      # TypeScript types
│   └── package.json
│
├── agents/              # AI Agent implementations
│   ├── fraud_agents/   # Custom agent package
│   │   ├── orchestrator/        # Main coordinator
│   │   ├── rag_agent/          # Policy retrieval
│   │   ├── transaction_analyst/ # Transaction analysis
│   │   ├── fraud_investigator/ # Risk assessment
│   │   ├── extensions/         # LiteLLM wrapper
│   │   └── shared/             # Shared utilities
│   └── pyproject.toml
│
├── ingestion/          # Document ingestion pipeline
│   ├── pipeline/
│   │   ├── embedder.py          # Bedrock Titan embeddings
│   │   ├── redis_indexer.py    # Vector index setup
│   │   └── unstructured_parser.py # S3 document parsing
│   └── pyproject.toml
│
├── k8s/                # Kubernetes manifests
│   ├── base/          # Common resources
│   ├── minikube/      # Local dev overlay
│   └── eks/           # AWS prod overlay
│
└── test_agents.py     # Integration test suite
```

## Configuration

### Environment Variables

Create `backend/.env`:

```bash
# Development mode (bypasses auth)
DEV_MODE=True

# Redis
REDIS_HOST=localhost
REDIS_TLS_PORT=6379

# AWS
AWS_REGION=us-east-1

# Cognito (for production auth)
COGNITO_USER_POOL_ID=us-east-1_XXXXXXX
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxx

# MLflow
MLFLOW_TRACKING_URI=sqlite:///mlflow.db

# CORS
ALLOWED_ORIGINS=["http://localhost:5173"]
```

### AWS Bedrock Setup

1. Enable model access in AWS Bedrock console:
   - Amazon Nova Lite
   - Claude 3 Haiku
   - Titan Embed Text v2

2. Create IAM role with permissions:
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "bedrock:InvokeModel",
       "bedrock:InvokeModelWithResponseStream"
     ],
     "Resource": "*"
   }
   ```

3. Configure AWS credentials:
   ```bash
   aws configure
   # Or use IAM roles in EKS
   ```

## API Endpoints

### Customer Portal

- `POST /api/v1/dispute` - Submit dispute
- `GET /api/v1/dispute/{case_id}/stream` - Stream status updates (SSE)

### Analyst Dashboard

- `GET /api/v1/dashboard/cases` - List all cases
- `GET /api/v1/dashboard/metrics` - Agent performance metrics
- `GET /api/v1/dashboard/risk-heatmap` - Fraud risk visualization

### System

- `GET /health` - Health check
- `GET /` - API information
- `GET /docs` - OpenAPI documentation (dev mode only)

## Testing

```bash
# Run agent integration tests
python test_agents.py

# Test API endpoints
curl -X POST http://localhost:8000/api/v1/dispute \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "dev-customer-123",
    "transaction_id": "txn-001",
    "dispute_amount_usd": 299.99,
    "dispute_reason": "Unauthorized charge"
  }'
```

## Development Workflow

1. **Make code changes** in `backend/`, `frontend/`, or `agents/`
2. **Backend auto-reloads** with uvicorn `--reload`
3. **Frontend hot-reloads** with Vite HMR
4. **Test locally** with DEV_MODE=True
5. **Test in minikube** before deploying to EKS
6. **Deploy to EKS** for production testing
7. **Switch back to minikube** to save costs

## Monitoring

**Logs:**
```bash
# Backend logs
kubectl logs -f -n fraud-system deployment/backend

# View structured logs
tail -f backend/app.log | jq .
```

**MLflow Tracking:**
```bash
# Start MLflow UI
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Access at http://localhost:5000
```

**Redis Monitoring:**
```bash
redis-cli
> INFO stats
> KEYS dispute:*
```

## Security

- **Authentication**: AWS Cognito JWT (production)
- **Authorization**: Customer can only access own disputes
- **Rate Limiting**: 100 req/min per IP
- **CORS**: Strict origin allowlist
- **TLS**: Required for production Redis
- **Secrets**: Stored in AWS Secrets Manager (EKS)

## Cost Optimization

**Local Development** (Free):
- Minikube
- Local Redis
- SQLite MLflow

**AWS Production** (Optimized):
- EKS with spot instances
- Cluster autoscaler
- Bedrock pay-per-use
- S3 Intelligent Tiering

**Recommended Usage Pattern:**
1. Develop locally with minikube
2. Test in EKS once per feature
3. Switch back to minikube
4. Only keep EKS running for production traffic

## Troubleshooting

### Common Issues

**"Address already in use" error:**
```bash
pkill -f uvicorn
lsof -ti:8000 | xargs kill -9
```

**Redis connection failed:**
```bash
docker ps | grep redis  # Check if running
redis-cli ping          # Test connectivity
```

**Import errors:**
```bash
cd backend && source .venv/bin/activate
uv pip install -e ".[dev]"
cd ../agents && uv pip install -e .
```

**Minikube not starting:**
```bash
minikube delete
minikube start --cpus=4 --memory=8192 --driver=docker
```

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Make changes with tests
3. Run test suite: `python test_agents.py`
4. Commit with clear messages
5. Create pull request

## License

Proprietary - Internal use only

## Support

Contact: fraud-team@example.com
