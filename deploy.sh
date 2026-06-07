#!/bin/bash
# Deployment script for Fraud Resolution System
# Supports both minikube (local) and EKS (AWS) deployments

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored message
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main deployment function
deploy() {
    local ENV=$1
    
    if [ "$ENV" != "minikube" ] && [ "$ENV" != "eks" ]; then
        print_error "Invalid environment. Use 'minikube' or 'eks'"
        echo "Usage: ./deploy.sh [minikube|eks]"
        exit 1
    fi
    
    print_info "Deploying to $ENV environment..."
    
    # Check prerequisites
    if ! command_exists kubectl; then
        print_error "kubectl not found. Please install kubectl first."
        exit 1
    fi
    
    if [ "$ENV" == "minikube" ]; then
        deploy_minikube
    else
        deploy_eks
    fi
}

# Deploy to minikube
deploy_minikube() {
    print_info "Starting minikube deployment..."
    
    # Check if minikube is installed
    if ! command_exists minikube; then
        print_error "minikube not found. Please install minikube first."
        echo "Install: https://minikube.sigs.k8s.io/docs/start/"
        exit 1
    fi
    
    # Start minikube if not running
    if ! minikube status >/dev/null 2>&1; then
        print_info "Starting minikube cluster..."
        minikube start --cpus=4 --memory=8192
    else
        print_info "Minikube is already running"
    fi
    
    # Build images in minikube's Docker daemon
    print_info "Building Docker images..."
    eval $(minikube docker-env)
    
    # Build backend image
    print_info "Building backend image..."
    docker build -t fraud-resolution-backend:latest ./backend
    
    # Apply Kubernetes manifests
    print_info "Applying Kubernetes manifests..."
    kubectl apply -k k8s/minikube
    
    # Wait for deployments to be ready
    print_info "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=backend -n fraud-system --timeout=300s || true
    kubectl wait --for=condition=ready pod -l app=redis -n fraud-system --timeout=300s || true
    
    # Get service URLs
    print_info "Deployment complete!"
    echo ""
    print_info "Access the application:"
    echo "  Backend API: minikube service backend -n fraud-system --url"
    echo "  Port forward: kubectl port-forward -n fraud-system svc/backend 8000:8000"
    echo ""
    echo "Then access:"
    echo "  API: http://localhost:8000"
    echo "  Docs: http://localhost:8000/docs"
}

# Deploy to EKS
deploy_eks() {
    print_info "Starting EKS deployment..."
    
    # Check if AWS CLI is installed
    if ! command_exists aws; then
        print_error "aws CLI not found. Please install AWS CLI first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=${AWS_REGION:-us-east-1}
    
    print_info "AWS Account: $AWS_ACCOUNT_ID"
    print_info "AWS Region: $AWS_REGION"
    
    # Check if ECR repository exists
    ECR_REPO="fraud-resolution-backend"
    if ! aws ecr describe-repositories --repository-names $ECR_REPO --region $AWS_REGION >/dev/null 2>&1; then
        print_info "Creating ECR repository..."
        aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION
    fi
    
    # Login to ECR
    print_info "Logging in to ECR..."
    aws ecr get-login-password --region $AWS_REGION | \
        docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Build and push backend image
    print_info "Building and pushing backend image..."
    docker build -t $ECR_REPO:latest ./backend
    docker tag $ECR_REPO:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest
    
    # Update image in deployment manifest
    sed -i.bak "s/<AWS_ACCOUNT_ID>/$AWS_ACCOUNT_ID/g" k8s/eks/backend-deployment.yaml
    
    # Apply Kubernetes manifests
    print_info "Applying Kubernetes manifests..."
    kubectl apply -k k8s/eks
    
    # Wait for deployments
    print_info "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=backend -n fraud-system --timeout=300s || true
    
    # Get load balancer URL
    print_info "Getting load balancer URL..."
    sleep 10  # Wait for LB to be created
    LB_URL=$(kubectl get svc backend -n fraud-system -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    
    # Restore original deployment file
    mv k8s/eks/backend-deployment.yaml.bak k8s/eks/backend-deployment.yaml
    
    print_info "Deployment complete!"
    echo ""
    print_info "Access the application:"
    echo "  Load Balancer: http://$LB_URL:8000"
    echo "  API Docs: http://$LB_URL:8000/docs"
    echo ""
    print_warn "Note: It may take a few minutes for the load balancer to become active."
}

# Check command line arguments
if [ $# -eq 0 ]; then
    echo "Fraud Resolution System - Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [minikube|eks]"
    echo ""
    echo "Environments:"
    echo "  minikube  - Deploy to local minikube cluster (free)"
    echo "  eks       - Deploy to AWS EKS cluster (production)"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh minikube    # Deploy locally"
    echo "  ./deploy.sh eks         # Deploy to AWS"
    exit 0
fi

# Run deployment
deploy $1
