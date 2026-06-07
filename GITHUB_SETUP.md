# Pushing to GitHub - Complete Setup Guide

## Prerequisites
- GitHub account: https://github.com/halloshrikant
- Git installed locally
- SSH key configured (recommended) or HTTPS credentials

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository settings:
   ```
   Owner: halloshrikant
   Repository name: fraud-resolution-system
   Description: AI-powered fraud dispute resolution using multi-agent orchestration with AWS Bedrock
   Visibility: ☑ Public (or Private if preferred)
   
   Do NOT initialize with:
   ☐ README
   ☐ .gitignore  
   ☐ License
   (We already have these files)
   ```
3. Click "Create repository"

## Step 2: Initialize Local Repository

```bash
cd /home/ubuntu

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Multi-agent fraud resolution system

Features:
- Multi-agent orchestration (RAG, Transaction Analyst, Fraud Investigator)
- AWS Bedrock integration (Nova, Claude, Titan)
- Redis Stack for vector search and session management
- FastAPI backend with SSE streaming
- React TypeScript frontend
- Kubernetes manifests (minikube + EKS)
- Comprehensive documentation
- GitHub Actions CI/CD
- MLflow experiment tracking
"
```

## Step 3: Add Remote and Push

```bash
# Add GitHub remote
git remote add origin https://github.com/halloshrikant/fraud-resolution-system.git

# Or with SSH (recommended):
git remote add origin git@github.com:halloshrikant/fraud-resolution-system.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Configure GitHub Settings

### A. Enable GitHub Pages (for documentation)

1. Go to repository Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages` (will be created by Actions)
4. Click Save

### B. Add Secrets (for CI/CD)

Go to Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

```
1. AWS_ACCESS_KEY_ID
   Value: Your AWS access key

2. AWS_SECRET_ACCESS_KEY
   Value: Your AWS secret key

3. DOCKER_USERNAME
   Value: Your Docker Hub username

4. DOCKER_PASSWORD
   Value: Your Docker Hub password or access token

5. SONAR_TOKEN (optional, for code quality)
   Value: SonarCloud token from https://sonarcloud.io
```

### C. Enable GitHub Actions

1. Go to repository Actions tab
2. Click "I understand my workflows, go ahead and enable them"
3. Workflows will run on next push

### D. Configure Branch Protection (recommended)

Settings → Branches → Add rule

```
Branch name pattern: main

Protection rules:
☑ Require a pull request before merging
  ☑ Require approvals (1)
☑ Require status checks to pass before merging
  ☑ Require branches to be up to date
  Status checks: 
    - Test Backend
    - Security Scan
☑ Require conversation resolution before merging
☐ Require signed commits (optional)
☑ Include administrators
```

## Step 5: Set Up Development Workflow

### A. Create Development Branch

```bash
# Create and switch to dev branch
git checkout -b develop

# Push to GitHub
git push -u origin develop
```

### B. Feature Branch Workflow

```bash
# For new features:
git checkout develop
git pull origin develop
git checkout -b feature/rag-agent-improvements

# Make changes...
git add .
git commit -m "feat: improve RAG agent policy retrieval"
git push origin feature/rag-agent-improvements

# Then create Pull Request on GitHub
```

### C. Commit Message Convention

Follow Conventional Commits:

```
Type: 
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- style: Code style (formatting, missing semi-colons)
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance tasks

Examples:
feat(agents): add Claude Sonnet fallback for complex cases
fix(api): resolve race condition in dispute submission
docs(readme): add architecture diagrams
refactor(orchestrator): simplify agent dispatch logic
test(agents): add integration tests for fraud investigator
chore(deps): upgrade FastAPI to 0.110.0
```

## Step 6: Verify Setup

### Check GitHub Actions

1. Go to Actions tab
2. You should see workflows running:
   - ✅ Backend CI/CD
   - ✅ Security Scanning
   - ✅ Documentation

### Check README

1. Visit repository page
2. Verify README.md renders correctly
3. Check badges (will show after first workflow run)

### Check Documentation

After GitHub Pages deploys:
1. Visit: https://halloshrikant.github.io/fraud-resolution-system
2. Verify docs are accessible

## Step 7: Add Badges to README

Add these badges to the top of README.md:

```markdown
# Fraud Resolution System 🛡️

[![CI/CD](https://github.com/halloshrikant/fraud-resolution-system/workflows/Backend%20CI%2FCD/badge.svg)](https://github.com/halloshrikant/fraud-resolution-system/actions)
[![Security](https://github.com/halloshrikant/fraud-resolution-system/workflows/Security%20Scanning/badge.svg)](https://github.com/halloshrikant/fraud-resolution-system/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green.svg)](https://fastapi.tiangolo.com/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
```

## Step 8: Clone Repository (others)

For others to clone:

```bash
git clone https://github.com/halloshrikant/fraud-resolution-system.git
cd fraud-resolution-system

# Follow QUICKSTART.md to set up
```

## Step 9: Continuous Deployment

### Automatic Deployment to EKS

When you push to `main` branch:

1. Tests run automatically
2. Docker image builds and pushes to Docker Hub
3. Kubernetes deployment updates in EKS
4. New pods roll out (zero-downtime)

View deployment status:
```bash
kubectl rollout status deployment/backend -n fraud-system
```

## Troubleshooting

### Issue: Push rejected (large files)

```bash
# Check file sizes
find . -type f -size +100M

# Remove large files from git
git rm --cached path/to/large/file
echo "path/to/large/file" >> .gitignore
git commit --amend -m "Remove large files"
git push -f origin main
```

### Issue: Workflow fails

1. Go to Actions tab
2. Click failed workflow
3. Expand failed step
4. Check error message
5. Fix locally and push again

### Issue: Authentication failed

```bash
# For HTTPS: Use Personal Access Token
# Generate at: https://github.com/settings/tokens
# Use token as password

# For SSH: Add SSH key
ssh-keygen -t ed25519 -C "your@email.com"
cat ~/.ssh/id_ed25519.pub
# Add to: https://github.com/settings/keys
```

## Next Steps

1. ✅ Code pushed to GitHub
2. ✅ CI/CD configured
3. ✅ Documentation live
4. 🔲 Invite collaborators
5. 🔲 Set up project board
6. 🔲 Create issue templates
7. 🔲 Add contributing guidelines

Your repository is now live at:
**https://github.com/halloshrikant/fraud-resolution-system** 🎉
