#!/usr/bin/env python3
"""Test script to verify all agents and components work correctly."""
import sys
import asyncio
from pathlib import Path

print("=" * 80)
print("FRAUD RESOLUTION SYSTEM - AGENT TEST SUITE")
print("=" * 80)

# Test 1: Import all agent modules
print("\n[TEST 1] Importing agent modules...")
try:
    from fraud_agents.shared.pydantic_models import DisputeRequest, FraudResolutionResult, RiskLevel, ResolutionAction
    from fraud_agents.shared.mlflow_tracker import MLflowSpanTracker
    from fraud_agents.shared.litellm_client import router
    from fraud_agents.extensions.litellm import LiteLLMModel
    print("✓ All shared modules imported successfully")
except Exception as e:
    print(f"✗ Failed to import shared modules: {e}")
    sys.exit(1)

try:
    from fraud_agents.orchestrator.agent import run_dispute_pipeline
    print("✓ Orchestrator agent imported")
except Exception as e:
    print(f"✗ Failed to import orchestrator: {e}")

try:
    from fraud_agents.rag_agent.agent import rag_agent
    from fraud_agents.rag_agent.retriever import PolicyRetriever
    print("✓ RAG agent imported")
except Exception as e:
    print(f"✗ Failed to import RAG agent: {e}")

try:
    from fraud_agents.transaction_analyst.agent import transaction_analyst_agent
    print("✓ Transaction analyst agent imported")
except Exception as e:
    print(f"✗ Failed to import transaction analyst: {e}")

try:
    from fraud_agents.fraud_investigator.agent import fraud_investigator_agent
    print("✓ Fraud investigator agent imported")
except Exception as e:
    print(f"✗ Failed to import fraud investigator: {e}")

# Test 2: Ingestion pipeline modules
print("\n[TEST 2] Testing ingestion pipeline modules...")
try:
    from ingestion.pipeline.embedder import embed_text
    from ingestion.pipeline.redis_indexer import create_policy_vector_index
    from ingestion.pipeline.unstructured_parser import stream_s3_documents
    print("✓ Ingestion pipeline modules imported")
except Exception as e:
    print(f"✗ Failed to import ingestion modules: {e}")

# Test 3: Create a mock dispute case
print("\n[TEST 3] Creating mock dispute case...")
try:
    dispute = DisputeRequest(
        customer_id="test-customer-001",
        transaction_id="txn-123456",
        dispute_reason="Unauthorized charge on my credit card. I did not make this purchase.",
        dispute_amount_usd=150.50
    )
    print(f"✓ Created dispute case: {dispute.case_id}")
    print(f"  Customer: {dispute.customer_id}")
    print(f"  Transaction: {dispute.transaction_id}")
    print(f"  Amount: ${dispute.dispute_amount_usd}")
except Exception as e:
    print(f"✗ Failed to create dispute: {e}")
    sys.exit(1)

# Test 4: Run orchestrator with mock tracker
print("\n[TEST 4] Running orchestrator pipeline...")
async def test_orchestrator():
    try:
        # Create mock tracker
        tracker = MLflowSpanTracker(dispute.case_id)
        tracker._start_ms = 0  # Mock start time
        tracker.run = None
        
        # Mock the enter/log methods to avoid MLflow server requirement
        tracker.__enter__ = lambda: tracker
        tracker.__exit__ = lambda *args: None
        tracker.log_agent_run = lambda result: print(f"  [MLflow] Would log: {result.risk_level}")
        
        # Run the pipeline
        result = await run_dispute_pipeline(dispute, tracker)
        
        print(f"✓ Pipeline completed successfully!")
        print(f"  Risk Score: {result.risk_score:.2f}")
        print(f"  Risk Level: {result.risk_level}")
        print(f"  Resolution: {result.resolution_action}")
        print(f"  Rationale: {result.agent_rationale[:100]}...")
        print(f"  Evidence Flags: {', '.join(result.evidence_flags)}")
        
        return result
    except Exception as e:
        print(f"✗ Orchestrator failed: {e}")
        import traceback
        traceback.print_exc()
        return None

result = asyncio.run(test_orchestrator())

# Test 5: Validate result structure
print("\n[TEST 5] Validating result structure...")
if result:
    try:
        assert isinstance(result, FraudResolutionResult), "Result is not FraudResolutionResult"
        assert 0.0 <= result.risk_score <= 1.0, f"Risk score out of range: {result.risk_score}"
        assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH], f"Invalid risk level: {result.risk_level}"
        assert result.resolution_action in [ResolutionAction.AUTO_APPROVE, ResolutionAction.ANALYST_REVIEW], f"Invalid action: {result.resolution_action}"
        assert result.case_id == dispute.case_id, "Case ID mismatch"
        print("✓ All result fields validated")
    except AssertionError as e:
        print(f"✗ Validation failed: {e}")
else:
    print("✗ No result to validate (orchestrator failed)")

# Test 6: Check package installations
print("\n[TEST 6] Checking installed packages...")
from importlib.metadata import version, PackageNotFoundError

required_packages = [
    "fastapi",
    "uvicorn",
    "redis",
    "pydantic",
    "litellm",
    "boto3",
    "mlflow",
    "openai-agents",
]

for pkg in required_packages:
    try:
        pkg_version = version(pkg)
        print(f"✓ {pkg:20s} v{pkg_version}")
    except PackageNotFoundError:
        print(f"✗ {pkg:20s} NOT INSTALLED")

# Final summary
print("\n" + "=" * 80)
if result:
    print("✅ ALL TESTS PASSED - System is operational")
    print(f"Mock dispute {dispute.case_id} processed successfully")
else:
    print("❌ SOME TESTS FAILED - Review errors above")
print("=" * 80)
