#!/bin/bash
# Verification script - Checks that all components are working correctly

set -e

echo "=============================================="
echo "  Fraud Resolution System - Verification"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1"
        ((FAILED++))
    fi
}

echo "1. Checking documentation..."
[ -f "README.md" ]; check "README.md exists"
[ -f "QUICKSTART.md" ]; check "QUICKSTART.md exists"
[ -f "SUMMARY.md" ]; check "SUMMARY.md exists"
[ -f "deploy.sh" ] && [ -x "deploy.sh" ]; check "deploy.sh is executable"

echo ""
echo "2. Checking project structure..."
[ -d "backend/app" ]; check "Backend directory structure"
[ -d "agents/fraud_agents" ]; check "Agents directory structure"
[ -d "k8s/base" ] && [ -d "k8s/minikube" ] && [ -d "k8s/eks" ]; check "Kubernetes manifests"
[ -f "backend/.env.example" ]; check "Environment config template"

echo ""
echo "3. Checking backend API..."
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    check "Backend is running"
    
    # Check root endpoint
    RESPONSE=$(curl -s http://127.0.0.1:8000/)
    if echo "$RESPONSE" | grep -q "Fraud Resolution API"; then
        check "Root endpoint working"
    else
        echo -e "${RED}✗${NC} Root endpoint not working"
        ((FAILED++))
    fi
    
    # Check docs
    if curl -s http://127.0.0.1:8000/docs | grep -q "swagger"; then
        check "OpenAPI docs enabled"
    else
        echo -e "${RED}✗${NC} OpenAPI docs not accessible"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗${NC} Backend not running"
    echo "  → Start with: cd backend && uvicorn app.main:app --reload"
    ((FAILED++))
fi

echo ""
echo "4. Checking Python packages..."
if [ -d "backend/.venv" ]; then
    check "Virtual environment exists"
    
    source backend/.venv/bin/activate 2>/dev/null
    if python -c "import fastapi" 2>/dev/null; then
        check "FastAPI installed"
    else
        echo -e "${RED}✗${NC} FastAPI not installed"
        ((FAILED++))
    fi
    
    if python -c "from fraud_agents.orchestrator.agent import run_dispute_pipeline" 2>/dev/null; then
        check "Agents package installed"
    else
        echo -e "${RED}✗${NC} Agents package not installed"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗${NC} Virtual environment not found"
    echo "  → Create with: cd backend && python -m venv .venv"
    ((FAILED++))
fi

echo ""
echo "5. Checking Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null || docker exec fraud-redis redis-cli ping &> /dev/null; then
        check "Redis is running"
    else
        echo -e "${RED}✗${NC} Redis not responding"
        echo "  → Start with: docker run -d -p 6379:6379 --name fraud-redis redis/redis-stack"
        ((FAILED++))
    fi
else
    echo "⚠  redis-cli not found, skipping Redis check"
fi

echo ""
echo "6. Checking Kubernetes setup..."
if [ -f "k8s/minikube/kustomization.yaml" ]; then
    check "Minikube manifests configured"
else
    echo -e "${RED}✗${NC} Minikube manifests missing"
    ((FAILED++))
fi

if [ -f "k8s/eks/kustomization.yaml" ]; then
    check "EKS manifests configured"
else
    echo -e "${RED}✗${NC} EKS manifests missing"
    ((FAILED++))
fi

echo ""
echo "=============================================="
echo "  Results: $PASSED passed, $FAILED failed"
echo "=============================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! System is ready.${NC}"
    echo ""
    echo "Next steps:"
    echo "  → View docs: open http://127.0.0.1:8000/docs"
    echo "  → Run tests: python test_agents.py"
    echo "  → Deploy to minikube: ./deploy.sh minikube"
    exit 0
else
    echo -e "${RED}⚠ Some checks failed. Review errors above.${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  → Setup: See QUICKSTART.md"
    echo "  → Troubleshooting: See QUICKSTART.md#troubleshooting"
    exit 1
fi
