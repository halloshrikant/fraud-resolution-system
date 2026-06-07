# Contributing to Fraud Resolution System

Thank you for considering contributing to this project! This guide will help you get started.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

**Key principles:**
- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

## Getting Started

### 1. Fork the Repository

Click the "Fork" button at the top right of the repository page.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/fraud-resolution-system.git
cd fraud-resolution-system
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/halloshrikant/fraud-resolution-system.git
git remote -v
```

### 4. Set Up Development Environment

Follow [QUICKSTART.md](QUICKSTART.md) to set up your local development environment.

### 5. Create a Feature Branch

```bash
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name
```

## Development Workflow

### Branch Naming Convention

```
feature/    - New features (feature/add-rag-caching)
fix/        - Bug fixes (fix/redis-connection-leak)
docs/       - Documentation (docs/update-api-guide)
refactor/   - Code refactoring (refactor/simplify-orchestrator)
test/       - Test additions (test/agent-integration)
chore/      - Maintenance (chore/upgrade-dependencies)
```

### Making Changes

1. **Write code** following our [coding standards](#coding-standards)
2. **Add tests** for new functionality
3. **Update documentation** if needed
4. **Run tests locally**:
   ```bash
   python test_agents.py
   ```
5. **Run linters**:
   ```bash
   ruff check .
   black .
   mypy app
   ```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(rag): implement semantic caching for policy retrieval

- Add TTL-based cache for embedding lookups
- Reduce average retrieval time from 500ms to 50ms
- Configure cache size limit to 10,000 entries

Closes #123
```

```
fix(api): resolve race condition in dispute submission

Multiple concurrent requests for same transaction_id could
create duplicate cases. Added distributed lock using Redis.

Fixes #456
```

## Pull Request Process

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with `develop`

### Submitting PR

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub:
   - Base: `develop` (not `main`)
   - Compare: `feature/your-feature-name`

3. **Fill out PR template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   How was this tested?

   ## Checklist
   - [ ] Tests pass
   - [ ] Documentation updated
   - [ ] No breaking changes
   ```

### PR Review Process

1. **Automated checks** run (CI/CD, security scan)
2. **Reviewer assigned** automatically
3. **Code review** (expect feedback within 48 hours)
4. **Address comments** by pushing new commits
5. **Approval** from at least 1 maintainer
6. **Merge** (squash and merge to `develop`)

### After Merge

1. Delete feature branch:
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. Update your fork:
   ```bash
   git checkout develop
   git pull upstream develop
   git push origin develop
   ```

## Coding Standards

### Python (Backend/Agents)

**Style Guide:** [PEP 8](https://pep8.org/) + [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

**Tools:**
- `black` - Auto-formatter
- `ruff` - Linter
- `mypy` - Type checker

**Key Rules:**

1. **Type Hints** (mandatory):
   ```python
   def process_dispute(
       dispute: DisputeRequest,
       customer_id: str
   ) -> FraudResolutionResult:
       ...
   ```

2. **Docstrings** (Google style):
   ```python
   def calculate_risk_score(transaction: Transaction) -> float:
       """Calculate fraud risk score for a transaction.
       
       Args:
           transaction: Transaction object with amount, location, timestamp
       
       Returns:
           Risk score between 0.0 (safe) and 1.0 (fraudulent)
       
       Raises:
           ValueError: If transaction amount is negative
       
       Example:
           >>> txn = Transaction(amount=99.99, location="NYC")
           >>> calculate_risk_score(txn)
           0.23
       """
       ...
   ```

3. **Error Handling**:
   ```python
   # ✅ GOOD: Specific exceptions
   try:
       result = await agent.run()
   except BedrockTimeoutError as e:
       logger.error(f"Bedrock timeout: {e}")
       raise HTTPException(status_code=504, detail="Agent timeout")
   except Exception as e:
       logger.exception(f"Unexpected error: {e}")
       raise
   
   # ❌ BAD: Bare except
   try:
       result = await agent.run()
   except:
       pass  # Swallows errors!
   ```

4. **Logging**:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   # Use appropriate levels
   logger.debug("Detailed debugging info")
   logger.info("Dispute submitted: %s", case_id)
   logger.warning("Redis latency high: %dms", latency)
   logger.error("Failed to retrieve policy: %s", error)
   logger.exception("Unhandled exception")  # Includes traceback
   ```

### TypeScript (Frontend)

**Style Guide:** [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)

**Tools:**
- `ESLint` - Linter
- `Prettier` - Formatter

**Key Rules:**

1. **Type Safety**:
   ```typescript
   // ✅ GOOD: Explicit types
   interface DisputeResponse {
     case_id: string;
     status: "PENDING" | "RESOLVED";
     risk_score?: number;
   }
   
   const submitDispute = async (
     data: DisputeRequest
   ): Promise<DisputeResponse> => {
     ...
   };
   
   // ❌ BAD: Any types
   const submitDispute = async (data: any): Promise<any> => {
     ...
   };
   ```

2. **React Hooks**:
   ```typescript
   // ✅ GOOD: Custom hooks for reusability
   const useDisputeStream = (caseId: string) => {
     const [status, setStatus] = useState<CaseStatus>("PENDING");
     
     useEffect(() => {
       const eventSource = new EventSource(`/api/v1/dispute/${caseId}/stream`);
       eventSource.onmessage = (event) => {
         setStatus(JSON.parse(event.data).status);
       };
       return () => eventSource.close();
     }, [caseId]);
     
     return status;
   };
   ```

### Project Structure

```
Backend modules:
backend/app/
├── api/          # HTTP endpoints (thin layer)
├── services/     # Business logic (thick layer)
├── models/       # Pydantic models
└── middleware/   # Cross-cutting concerns

Agents modules:
agents/fraud_agents/
├── orchestrator/      # Main coordinator
├── rag_agent/        # Policy retrieval
├── extensions/       # Framework extensions
└── shared/           # Shared utilities

Tests:
tests/
├── unit/         # Unit tests (fast, isolated)
├── integration/  # Integration tests (DB, agents)
└── e2e/          # End-to-end tests (full flow)
```

## Testing Guidelines

### Test Structure

```python
# test_fraud_investigator.py
import pytest
from fraud_agents.fraud_investigator.agent import assess_risk

class TestFraudInvestigator:
    """Test suite for fraud investigator agent."""
    
    @pytest.fixture
    def sample_transaction(self):
        """Fixture: Sample transaction data."""
        return Transaction(
            amount=299.99,
            location="New York, NY",
            timestamp="2026-06-07T14:30:00Z"
        )
    
    def test_high_amount_increases_risk(self, sample_transaction):
        """High transaction amounts should increase risk score."""
        sample_transaction.amount = 5000.00
        risk = assess_risk(sample_transaction)
        assert risk > 0.7, "High amount should have high risk"
    
    @pytest.mark.asyncio
    async def test_bedrock_timeout_handling(self):
        """Should handle Bedrock timeouts gracefully."""
        with pytest.raises(BedrockTimeoutError):
            await agent.run(timeout=0.001)  # Force timeout
```

### Test Coverage

Aim for **80%+ coverage**:

```bash
# Run with coverage
pytest --cov=backend --cov=agents --cov-report=html

# View report
open htmlcov/index.html
```

### Test Categories

1. **Unit Tests**: Fast, isolated, no external dependencies
2. **Integration Tests**: Test with Redis, Bedrock (mocked)
3. **E2E Tests**: Full flow from API to resolution

## Documentation

### What to Document

1. **Code**: Docstrings for all public functions/classes
2. **API**: Update OpenAPI schema if endpoints change
3. **Architecture**: Update diagrams if structure changes
4. **User Guide**: Update QUICKSTART.md for new features

### Documentation Structure

```
docs/
├── architecture/
│   ├── system-design.md
│   ├── data-flow.md
│   └── diagrams/
├── api/
│   ├── endpoints.md
│   └── authentication.md
├── guides/
│   ├── local-development.md
│   ├── deployment.md
│   └── troubleshooting.md
└── interview/
    └── qa.md
```

## Questions?

- **General**: Open a [Discussion](https://github.com/halloshrikant/fraud-resolution-system/discussions)
- **Bug**: Open an [Issue](https://github.com/halloshrikant/fraud-resolution-system/issues)
- **Security**: Email security@example.com (do NOT open public issue)

## Recognition

Contributors will be listed in [CONTRIBUTORS.md](CONTRIBUTORS.md).

Thank you for contributing! 🎉
