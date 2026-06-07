#!/bin/bash
# Automated GitHub Push Script
# Usage: ./push-to-github.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Fraud Resolution System - GitHub Push                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if already initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo -e "${GREEN}✓${NC} Git initialized"
else
    echo -e "${GREEN}✓${NC} Git already initialized"
fi

# Add all files
echo ""
echo "📝 Staging files..."
git add .

# Show status
echo ""
echo "📊 Files to be committed:"
git status --short

# Get commit message
echo ""
read -p "📝 Enter commit message (or press Enter for default): " COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Initial commit: Multi-agent fraud resolution system

Features:
- Multi-agent orchestration (RAG, Transaction Analyst, Fraud Investigator)
- AWS Bedrock integration (Nova, Claude, Titan)
- Redis Stack for vector search and session management
- FastAPI backend with SSE streaming
- React TypeScript frontend
- Kubernetes manifests (minikube + EKS)
- Comprehensive documentation (800+ lines)
- GitHub Actions CI/CD
- MLflow experiment tracking
- Interview Q&A documentation"
fi

# Commit
echo ""
echo "💾 Creating commit..."
git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✓${NC} Committed"

# Check for existing remote
if git remote | grep -q 'origin'; then
    echo -e "${YELLOW}⚠${NC} Remote 'origin' already exists"
    git remote -v
    read -p "Do you want to remove and re-add it? (y/N): " REMOVE_REMOTE
    if [ "$REMOVE_REMOTE" = "y" ] || [ "$REMOVE_REMOTE" = "Y" ]; then
        git remote remove origin
        echo "Removed existing remote"
    fi
fi

# Add remote if not exists
if ! git remote | grep -q 'origin'; then
    echo ""
    echo "🔗 GitHub repository URL options:"
    echo "  1. HTTPS: https://github.com/halloshrikant/fraud-resolution-system.git"
    echo "  2. SSH:   git@github.com:halloshrikant/fraud-resolution-system.git"
    echo ""
    read -p "Enter repository URL (or press Enter for default HTTPS): " REPO_URL
    
    if [ -z "$REPO_URL" ]; then
        REPO_URL="https://github.com/halloshrikant/fraud-resolution-system.git"
    fi
    
    echo "Adding remote: $REPO_URL"
    git remote add origin "$REPO_URL"
    echo -e "${GREEN}✓${NC} Remote added"
fi

# Rename branch to main if needed
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "📌 Renaming branch to 'main'..."
    git branch -M main
fi

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
echo "This will push to: $(git remote get-url origin)"
echo ""
read -p "Continue with push? (Y/n): " CONFIRM_PUSH

if [ "$CONFIRM_PUSH" = "n" ] || [ "$CONFIRM_PUSH" = "N" ]; then
    echo "Push cancelled. You can push manually later with:"
    echo "  git push -u origin main"
    exit 0
fi

echo ""
echo "Pushing..."
if git push -u origin main; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ✅ SUCCESS! Code pushed to GitHub                        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🎉 Your repository is now live at:"
    echo "   https://github.com/halloshrikant/fraud-resolution-system"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Configure GitHub secrets (see GITHUB_SETUP.md)"
    echo "  2. Enable GitHub Actions"
    echo "  3. Set up branch protection"
    echo "  4. Invite collaborators"
    echo ""
    echo "📚 Documentation available at:"
    echo "  - README.md         - Project overview"
    echo "  - QUICKSTART.md     - Setup guide"
    echo "  - INTERVIEW_QA.md   - Interview Q&A"
    echo "  - CONTRIBUTING.md   - Contribution guide"
    echo ""
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo ""
    echo "  1. Repository doesn't exist on GitHub"
    echo "     → Create it at: https://github.com/new"
    echo ""
    echo "  2. Authentication failed"
    echo "     → HTTPS: Use Personal Access Token as password"
    echo "     → SSH: Add SSH key to GitHub"
    echo ""
    echo "  3. Branch protection rules"
    echo "     → Push to a different branch first"
    echo ""
    echo "See GITHUB_SETUP.md for detailed instructions"
    exit 1
fi
