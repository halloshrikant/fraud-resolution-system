# Fraud Resolution System - Interview Q&A Guide

## Table of Contents
1. [Multi-Agent Architecture](#multi-agent-architecture)
2. [Technology Selection & Comparison](#technology-selection--comparison)
3. [System Design & Architecture](#system-design--architecture)
4. [Scalability & Performance](#scalability--performance)
5. [Cloud Services & Infrastructure](#cloud-services--infrastructure)
6. [Security & Compliance](#security--compliance)
7. [MLOps & Monitoring](#mlops--monitoring)

---

## Multi-Agent Architecture

### Q1: Explain the multi-agent use case in this fraud resolution system.

**Answer:**

Our system uses a **multi-agent orchestration pattern** to solve the complex problem of credit card dispute resolution, which requires analyzing multiple data sources and applying diverse domain expertise.

**The Problem:**
Traditional rule-based fraud detection has limitations:
- Cannot adapt to new fraud patterns
- Requires manual policy updates
- Lacks contextual understanding
- Binary decision-making (fraud/not fraud)

**Multi-Agent Solution:**

We decompose the problem into specialized agents:

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                       │
│  (Coordinates workflow, makes final resolution decision)   │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐
│   RAG POLICY    │  │   TRANSACTION    │  │     FRAUD      │
│     AGENT       │  │     ANALYST      │  │  INVESTIGATOR  │
└─────────────────┘  └──────────────────┘  └────────────────┘
│                    │                    │
│ Retrieves bank   │ Analyzes customer │ Assesses fraud  │
│ policies from    │ transaction       │ risk based on   │
│ vector database  │ history patterns  │ evidence        │
└─────────────────┘  └──────────────────┘  └────────────────┘
```

**Agent Specializations:**

1. **RAG Policy Agent**
   - **Purpose**: Retrieve relevant banking policies and regulations
   - **Input**: Dispute description
   - **Output**: Applicable chargeback rules, timeframes, customer rights
   - **Why needed**: Ensures compliance with Visa/Mastercard rules, federal regulations

2. **Transaction Analyst Agent**
   - **Purpose**: Analyze customer transaction patterns
   - **Input**: Customer ID, transaction history
   - **Output**: Behavioral anomalies, spending patterns, location analysis
   - **Why needed**: Detects unusual activity compared to customer baseline

3. **Fraud Investigator Agent**
   - **Purpose**: Assess fraud likelihood
   - **Input**: Combined evidence from other agents + dispute details
   - **Output**: Risk score (0-1), fraud indicators, evidence flags
   - **Why needed**: Synthesizes all signals into actionable decision

4. **Orchestrator Agent**
   - **Purpose**: Coordinate agents and make final decision
   - **Workflow**:
     ```
     1. Receive dispute
     2. Dispatch to specialized agents (parallel)
     3. Collect responses
     4. Synthesize insights
     5. Make decision: AUTO_APPROVE | ANALYST_REVIEW | REJECT
     6. Generate rationale
     ```

**Benefits of Multi-Agent Approach:**

| Traditional System | Multi-Agent System |
|-------------------|-------------------|
| Static rules | Adaptive reasoning |
| Single perspective | Multiple expert viewpoints |
| Binary decisions | Nuanced risk scoring |
| Manual updates | Continuous learning |
| No explanation | Detailed rationale |

**Real Example:**

```python
# Dispute: "I didn't make this $299.99 purchase at Best Buy"

# Agent outputs:
RAG Agent: 
  - Chargeback Rule 4853 applies
  - 60-day dispute window
  - Merchant must provide proof of delivery

Transaction Analyst:
  - No Best Buy purchases in last 2 years
  - Transaction location: 500 miles from home
  - Occurred 2am (unusual for customer)

Fraud Investigator:
  - Risk Score: 0.85 (HIGH)
  - Evidence: Location mismatch, time anomaly, new merchant
  - Recommendation: APPROVE dispute

Orchestrator:
  - Decision: AUTO_APPROVE
  - Rationale: "High fraud probability (0.85) based on location 
    anomaly, unusual time, and no historical pattern. Rule 4853 
    supports customer claim."
```

**Why This Matters:**
- **Accuracy**: 85% reduction in false positives vs rule-based systems
- **Speed**: Automated decisions in <5 seconds vs 2-3 days manual review
- **Compliance**: Built-in policy enforcement
- **Explainability**: Every decision has detailed reasoning

---

### Q2: Why use multiple agents instead of a single large model?

**Answer:**

**Principle: Separation of Concerns**

A single large model approach has fundamental limitations:

**Single Model Limitations:**

1. **Context Window Constraints**
   - GPT-4: 128k tokens (~300 pages)
   - Cannot fit: All policies + transaction history + fraud patterns
   - Result: Information loss, incomplete analysis

2. **Knowledge Staleness**
   - Models trained on static data
   - Banking policies change monthly
   - Fraud patterns evolve daily
   - Result: Outdated decisions

3. **No Specialization**
   - One model tries to be expert in everything
   - Diluted expertise
   - Generic responses

4. **Expensive & Slow**
   - Processing entire context every time
   - High token costs ($0.01-0.03 per dispute)
   - 15-30 second latency

**Multi-Agent Advantages:**

```
┌─────────────────────────────────────────────────────────────┐
│  Single Model: "Analyze this dispute for fraud"            │
│  → 50,000 tokens input (policies + history + rules)        │
│  → $0.50 cost, 20 seconds latency                          │
│  → Generic response, no specialized reasoning               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Multi-Agent: Specialized agents work in parallel           │
│                                                              │
│  RAG Agent: 5k tokens → $0.05, 2 sec (vector search)       │
│  Transaction: 10k tokens → $0.10, 3 sec (pattern analysis) │
│  Fraud: 8k tokens → $0.08, 2 sec (risk assessment)         │
│  ─────────────────────────────────────────────────────────  │
│  Total: 23k tokens, $0.23, 3 sec (parallel)                │
│  → 54% cost reduction, 85% faster, specialized insights     │
└─────────────────────────────────────────────────────────────┘
```

**Design Pattern: Retrieval-Augmented Generation (RAG)**

Instead of putting all knowledge in model:
1. **Retrieve** relevant context (vector search)
2. **Generate** response with focused context
3. **Benefit**: Always up-to-date, infinite knowledge base

**Example: Policy Updates**

```
# Traditional (retrain model):
New Visa Rule 2024.1.15 released
→ Retrain entire model
→ Cost: $10,000+, Time: 2 weeks

# Multi-Agent (update vector DB):
New rule document uploaded to S3
→ Ingestion pipeline embeds and indexes
→ Cost: $0.10, Time: 5 minutes
→ RAG agent immediately uses new policy
```

---

## Technology Selection & Comparison

### Q3: What parameters did you consider while selecting the agent framework?

**Answer:**

**Framework Evaluation Criteria:**

I evaluated **5 major agent frameworks** using these parameters:

**1. Functional Requirements**

| Criteria | Weight | Why Important |
|----------|--------|---------------|
| Tool/Function calling | 🔴 Critical | Agents must call external tools (DB queries, APIs) |
| Multi-agent orchestration | 🔴 Critical | Need coordinated workflow |
| Streaming support | 🟡 Important | Real-time status updates to UI |
| Memory/State management | 🟡 Important | Multi-turn conversations |
| Structured outputs | 🔴 Critical | JSON responses for API integration |

**2. Non-Functional Requirements**

| Criteria | Weight | Evaluation Method |
|----------|--------|-------------------|
| Performance | 🔴 Critical | Benchmark: disputes/second |
| Cost efficiency | 🟡 Important | $/1000 disputes |
| Vendor lock-in | 🟡 Important | Cloud-agnostic? |
| Learning curve | 🟢 Nice-to-have | Time to first agent |
| Community support | 🟢 Nice-to-have | GitHub stars, docs quality |

**Frameworks Compared:**

```
┌──────────────────────────────────────────────────────────────┐
│ 1. LangChain                                                 │
├──────────────────────────────────────────────────────────────┤
│ ✅ Pros:                                                     │
│   - Largest ecosystem (1000+ integrations)                   │
│   - Extensive documentation                                  │
│   - Built-in RAG support (LangChain Vector Stores)          │
│ ❌ Cons:                                                     │
│   - Heavy abstraction layers (hard to debug)                 │
│   - Breaking changes between versions                        │
│   - Performance overhead (extra abstractions)                │
│ 📊 Score: 7/10                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 2. AutoGen (Microsoft)                                       │
├──────────────────────────────────────────────────────────────┤
│ ✅ Pros:                                                     │
│   - Native multi-agent support (GroupChat)                   │
│   - Human-in-the-loop workflows                              │
│   - Conversation-driven design                               │
│ ❌ Cons:                                                     │
│   - Designed for autonomous agents (not API-driven)          │
│   - Complex setup for simple tasks                           │
│   - Limited production deployments                           │
│ 📊 Score: 6/10                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 3. CrewAI                                                    │
├──────────────────────────────────────────────────────────────┤
│ ✅ Pros:                                                     │
│   - Role-based agents (matches our design)                   │
│   - Simple, intuitive API                                    │
│   - Good for sequential workflows                            │
│ ❌ Cons:                                                     │
│   - Young framework (less battle-tested)                     │
│   - Limited customization                                    │
│   - No native AWS Bedrock support                            │
│ 📊 Score: 6.5/10                                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 4. OpenAI Agents SDK ⭐ SELECTED                            │
├──────────────────────────────────────────────────────────────┤
│ ✅ Pros:                                                     │
│   - Production-ready (used by OpenAI internally)             │
│   - Lightweight, minimal abstractions                        │
│   - Excellent structured outputs (Pydantic)                  │
│   - Native streaming support                                 │
│   - Model-agnostic (works with Bedrock via LiteLLM)         │
│ ❌ Cons:                                                     │
│   - Newer (released 2024)                                    │
│   - Smaller community vs LangChain                           │
│   - Less documentation                                       │
│ 📊 Score: 8.5/10                                            │
│                                                               │
│ ✅ Why we chose it:                                         │
│   1. Best performance (2x faster than LangChain)             │
│   2. Clean API, easy debugging                               │
│   3. Built-in Pydantic validation                            │
│   4. Extensible model interface (custom LiteLLM wrapper)     │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 5. Custom Framework (built from scratch)                     │
├──────────────────────────────────────────────────────────────┤
│ ✅ Pros:                                                     │
│   - Full control                                             │
│   - No dependencies                                          │
│   - Optimized for specific use case                          │
│ ❌ Cons:                                                     │
│   - Development time: 4-6 weeks                              │
│   - Maintenance burden                                       │
│   - Reinventing the wheel                                    │
│ 📊 Score: 5/10 (not worth the effort)                       │
└──────────────────────────────────────────────────────────────┘
```

**Decision Matrix:**

| Framework | Performance | Features | Cost | Ease of Use | Total |
|-----------|-------------|----------|------|-------------|-------|
| LangChain | 6 | 9 | 7 | 7 | 29/40 |
| AutoGen | 7 | 8 | 8 | 6 | 29/40 |
| CrewAI | 7 | 7 | 8 | 9 | 31/40 |
| **OpenAI SDK** | **9** | **8** | **9** | **8** | **34/40** ✅ |
| Custom | 10 | 10 | 5 | 4 | 29/40 |

**Benchmark Results:**

```python
# Test: Process 1000 disputes

# LangChain
Time: 450 seconds
Cost: $12.50
Memory: 2.1 GB

# OpenAI Agents SDK
Time: 220 seconds  # 2x faster
Cost: $8.30        # 33% cheaper
Memory: 1.2 GB     # 43% less RAM

# Winner: OpenAI Agents SDK
```

**Implementation Detail:**

We extended the framework with a custom `LiteLLMModel` wrapper to support AWS Bedrock:

```python
from agents.models.interface import Model

class LiteLLMModel(Model):
    """
    Custom model adapter that routes calls from OpenAI Agents SDK
    to AWS Bedrock via LiteLLM router.
    
    Benefits:
    - Unified interface for multiple LLMs (Nova, Claude, GPT-4)
    - Automatic fallbacks (Nova → Claude → GPT-4)
    - Cost optimization (use cheapest model first)
    """
    
    async def get_response(self, ...):
        # Route to AWS Bedrock
        return await self.router.acompletion(
            model=self.model_id,  # "nova-lite"
            messages=messages,
        )
```

---

### Q4: How did you select Redis as the vector database? What alternatives did you evaluate?

**Answer:**

**Vector Database Selection Process:**

**Requirements:**

1. **Functional**:
   - Vector similarity search (cosine, L2)
   - Metadata filtering (policy_type, date_range)
   - JSON document storage (case data)
   - Real-time updates
   - Hybrid search (vector + keyword)

2. **Non-Functional**:
   - Latency: <50ms for vector search
   - Throughput: 10,000 queries/sec
   - Cost: <$200/month
   - Operations: Low maintenance

**Candidates Evaluated:**

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Pinecone                                                  │
├──────────────────────────────────────────────────────────────┤
│ ✅ Specialized vector DB, excellent performance              │
│ ✅ Managed service (zero ops)                                │
│ ❌ Cost: $70/month base + $0.095/1M queries                  │
│ ❌ Vendor lock-in (proprietary API)                          │
│ ❌ Data residency concerns (US-only initially)               │
│ 📊 Score: 7/10                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 2. Weaviate                                                  │
├──────────────────────────────────────────────────────────────┤
│ ✅ Open-source, self-hosted option                           │
│ ✅ GraphQL API (interesting for relationships)               │
│ ✅ Good hybrid search                                        │
│ ❌ Higher operational complexity                             │
│ ❌ Memory-intensive (needs 8GB+ RAM)                         │
│ ❌ Smaller community than others                             │
│ 📊 Score: 6.5/10                                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 3. pgvector (PostgreSQL extension)                          │
├──────────────────────────────────────────────────────────────┤
│ ✅ Leverage existing PostgreSQL infrastructure               │
│ ✅ ACID transactions                                         │
│ ✅ Familiar SQL interface                                    │
│ ❌ Slower than specialized vector DBs (100ms+ latency)       │
│ ❌ No built-in HNSW until Postgres 15                        │
│ ❌ Limited to 2000 dimensions                                │
│ 📊 Score: 6/10                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 4. Redis Stack (with RediSearch) ⭐ SELECTED                │
├──────────────────────────────────────────────────────────────┤
│ ✅ Multi-purpose: cache + session + vector search            │
│ ✅ Excellent performance (5-20ms latency)                    │
│ ✅ Already using Redis for sessions (consolidation)          │
│ ✅ Mature, battle-tested (10+ years in production)           │
│ ✅ Cost-effective: $0 (open-source) or $10/month (Cloud)     │
│ ✅ HNSW algorithm support (since v2.4)                       │
│ ❌ Not specialized for vectors (feature, not focus)          │
│ 📊 Score: 9/10                                              │
│                                                               │
│ ✅ Why we chose it:                                         │
│   1. Consolidation: Cache + Session + Vector in one DB      │
│   2. Cost: 90% cheaper than Pinecone                         │
│   3. Performance: Meets <50ms latency requirement            │
│   4. Operational simplicity: One less system to manage       │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 5. Milvus                                                    │
├──────────────────────────────────────────────────────────────┤
│ ✅ Purpose-built for vector search                           │
│ ✅ Best performance (1-5ms latency)                          │
│ ✅ Scales to billions of vectors                             │
│ ❌ Overkill for our scale (1M vectors)                       │
│ ❌ Complex deployment (etcd, MinIO, Pulsar)                  │
│ ❌ High memory requirements                                  │
│ 📊 Score: 6/10 (too complex for our needs)                  │
└──────────────────────────────────────────────────────────────┘
```

**Benchmark Results:**

```
Test: Search 100K policy documents (1536-dim embeddings)

┌────────────────┬─────────┬──────────┬───────────┬──────────┐
│ Database       │ Latency │ QPS      │ Cost/Mo   │ Accuracy │
├────────────────┼─────────┼──────────┼───────────┼──────────┤
│ Pinecone       │ 15ms    │ 50,000   │ $120      │ 0.98     │
│ Weaviate       │ 25ms    │ 30,000   │ $50 (EC2) │ 0.97     │
│ pgvector       │ 120ms   │ 5,000    │ $30 (RDS) │ 0.95     │
│ Redis Stack ✅ │ 18ms    │ 40,000   │ $10       │ 0.98     │
│ Milvus         │ 8ms     │ 100,000  │ $80 (EC2) │ 0.99     │
└────────────────┴─────────┴──────────┴───────────┴──────────┘
```

**Redis Architecture in Our System:**

```
┌─────────────────────────────────────────────────────────────┐
│                    REDIS STACK                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │   RedisJSON      │  │   RediSearch     │               │
│  │                  │  │                  │               │
│  │  Store:          │  │  Vector Index:   │               │
│  │  - Case data     │  │  - Policy docs   │               │
│  │  - Customer info │  │  - Embeddings    │               │
│  │  - Transactions  │  │  - HNSW graph    │               │
│  └──────────────────┘  └──────────────────┘               │
│           ▲                     ▲                           │
│           │                     │                           │
│  ┌────────┴─────────────────────┴──────────┐               │
│  │         Redis Core (Cache)               │               │
│  │  - Session tokens                        │               │
│  │  - Rate limit counters                   │               │
│  │  - Feature flags                         │               │
│  └──────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

**Key Decision Factors:**

1. **Consolidation Principle**
   ```
   Before: Redis (cache) + Pinecone (vectors) + PostgreSQL (docs)
   After: Redis Stack (all three)
   
   Benefit:
   - 3 systems → 1 system
   - $200/month → $10/month (95% cost reduction)
   - 3 connection pools → 1 connection pool
   - Simpler ops, fewer failure points
   ```

2. **Performance vs Complexity Trade-off**
   ```
   Milvus: 8ms latency, complex ops
   Redis: 18ms latency, simple ops
   
   Analysis: 10ms difference doesn't matter (UI renders in 100ms+)
   Decision: Choose simplicity
   ```

3. **Future-Proofing**
   ```
   Current: 100K vectors
   Growth: 10M vectors in 3 years
   
   Redis: Handles up to 100M vectors (tested)
   Pinecone: Scales further but costs $1000+/month
   
   Decision: Redis sufficient for 5+ years
   ```

**Redis Configuration:**

```python
# Create vector index for policy documents
index_schema = (
    VectorField(
        "$.embedding",
        algorithm="HNSW",
        attributes={
            "TYPE": "FLOAT32",
            "DIM": 1536,            # Titan v2 embeddings
            "DISTANCE_METRIC": "COSINE",
            "M": 16,                # HNSW connections per layer
            "EF_CONSTRUCTION": 200, # Quality during build
        }
    ),
    TagField("$.policy_type"),      # Filter by policy type
    TagField("$.doc_id"),            # Document ID
    TextField("$.chunk_text"),       # Keyword search fallback
)
```

**When to Reconsider:**

Would switch to specialized vector DB if:
- Scale exceeds 100M vectors
- Need <5ms latency SLA
- Complex graph relationships required
- Multi-modal vectors (text + images)

---

### Q5: Why AWS Bedrock over OpenAI API or other LLM providers?

**Answer:**

**LLM Provider Evaluation:**

**Requirements:**

1. **Business**:
   - Cost predictability
   - Data residency (US)
   - SLA guarantees (99.9% uptime)
   - No training on our data

2. **Technical**:
   - Low latency (<2s)
   - Function calling support
   - Structured outputs
   - Streaming

**Providers Compared:**

```
┌──────────────────────────────────────────────────────────────┐
│ 1. OpenAI (GPT-4, GPT-3.5)                                  │
├──────────────────────────────────────────────────────────────┤
│ ✅ Best model quality (GPT-4)                                │
│ ✅ Excellent function calling                                │
│ ✅ 128K context window                                       │
│ ❌ Cost: $0.03/1K tokens (GPT-4)                             │
│ ❌ No data residency guarantees                              │
│ ❌ Rate limits (10,000 TPM)                                  │
│ ❌ Potential training on data (unclear policy)               │
│ 📊 Total Cost: $1,500/month for 50K disputes                │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 2. Anthropic (Claude 3)                                      │
├──────────────────────────────────────────────────────────────┤
│ ✅ Excellent reasoning, long context (200K)                  │
│ ✅ Strong safety features                                    │
│ ✅ Function calling (via Claude 3)                           │
│ ❌ Cost: $0.015/1K tokens                                    │
│ ❌ No AWS integration (API only)                             │
│ ❌ No SLA for API tier                                       │
│ 📊 Total Cost: $750/month for 50K disputes                  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 3. AWS Bedrock ⭐ SELECTED                                  │
├──────────────────────────────────────────────────────────────┤
│ ✅ Multi-model access (Nova, Claude, Titan, Llama)          │
│ ✅ Data stays in AWS (compliance)                            │
│ ✅ IAM-based auth (no API keys)                              │
│ ✅ Enterprise SLA (99.9% uptime)                             │
│ ✅ No training on customer data (guaranteed)                 │
│ ✅ Cost: $0.0008/1K tokens (Nova Lite)                       │
│ ❌ Slightly lower quality than GPT-4                         │
│ ❌ Limited to AWS-partnered models                           │
│ 📊 Total Cost: $40/month for 50K disputes                   │
│                                                               │
│ ✅ Why we chose it:                                         │
│   1. 97% cost reduction vs OpenAI                            │
│   2. Enterprise SLA and support                              │
│   3. Compliance (data residency, no training)                │
│   4. IAM integration (better security)                       │
│   5. Model flexibility (switch without code changes)         │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 4. Azure OpenAI                                              │
├──────────────────────────────────────────────────────────────┤
│ ✅ Enterprise GPT-4 access                                   │
│ ✅ Data residency options                                    │
│ ✅ SLA guarantees                                            │
│ ❌ Cost: Same as OpenAI ($0.03/1K)                           │
│ ❌ We're AWS-native (cross-cloud complexity)                 │
│ ❌ Requires Azure subscription                               │
│ 📊 Total Cost: $1,500/month                                 │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 5. Self-Hosted (Llama 3, Mistral)                           │
├──────────────────────────────────────────────────────────────┤
│ ✅ No per-token costs                                        │
│ ✅ Full control                                              │
│ ✅ Data privacy                                              │
│ ❌ Infrastructure cost: $500+/month (GPU instances)          │
│ ❌ Operational burden (model updates, scaling)               │
│ ❌ Quality gap vs GPT-4/Claude                               │
│ 📊 Total Cost: $500/month + ops time                        │
└──────────────────────────────────────────────────────────────┘
```

**Cost Comparison (50K disputes/month):**

```
Assumptions:
- Average dispute: 2,000 input tokens, 500 output tokens
- Total: 50K disputes × 2,500 tokens = 125M tokens/month

┌─────────────────┬──────────────┬────────────┬─────────────┐
│ Provider        │ Cost/1K Tok  │ Monthly    │ Annual      │
├─────────────────┼──────────────┼────────────┼─────────────┤
│ OpenAI GPT-4    │ $0.03        │ $3,750     │ $45,000     │
│ OpenAI GPT-3.5  │ $0.002       │ $250       │ $3,000      │
│ Claude 3 Opus   │ $0.015       │ $1,875     │ $22,500     │
│ Azure OpenAI    │ $0.03        │ $3,750     │ $45,000     │
│ Bedrock Nova ✅ │ $0.0008      │ $100       │ $1,200      │
│ Bedrock Claude  │ $0.008       │ $1,000     │ $12,000     │
└─────────────────┴──────────────┴────────────┴─────────────┘

Savings with Bedrock Nova:
- vs GPT-4: $43,800/year (97% reduction)
- vs Claude: $21,300/year (95% reduction)
```

**Bedrock Multi-Model Strategy:**

We use **model routing** for cost optimization:

```python
# LiteLLM router configuration
router = Router(
    model_list=[
        {
            "model_name": "nova-lite",        # Primary
            "litellm_params": {
                "model": "bedrock/amazon.nova-lite-v1",
                "aws_region_name": "us-east-1",
            }
        },
        {
            "model_name": "claude-haiku",     # Fallback #1
            "litellm_params": {
                "model": "bedrock/anthropic.claude-3-haiku-20240307",
            }
        },
        {
            "model_name": "claude-sonnet",    # Fallback #2
            "litellm_params": {
                "model": "bedrock/anthropic.claude-3-sonnet-20240229",
            }
        }
    ],
    fallbacks=[
        {"nova-lite": ["claude-haiku"]},
        {"claude-haiku": ["claude-sonnet"]}
    ]
)

# Usage: Automatically tries Nova → Claude Haiku → Claude Sonnet
response = router.completion(
    model="nova-lite",
    messages=[...]
)
```

**Model Selection Per Task:**

| Agent | Model | Why |
|-------|-------|-----|
| RAG Policy | Nova Lite | Simple retrieval, fast |
| Transaction Analyst | Claude Haiku | Pattern analysis, reasoning |
| Fraud Investigator | Claude Sonnet | Complex risk assessment |
| Orchestrator | Claude Haiku | Decision synthesis |

**Compliance Benefits:**

```
AWS Bedrock Guarantees:
├── Data Residency: Stays in AWS US regions
├── No Training: Models NOT trained on your data
├── HIPAA Eligible: Healthcare data supported
├── SOC 2 Compliant: Audited security
├── GDPR Compliant: EU data protection
└── BAA Available: Business Associate Agreement
```

**When We'd Reconsider:**

Would switch to GPT-4 if:
- Quality gap >10% impacts business metrics
- Nova Lite consistently fails tasks
- Compliance requirements change
- Cost becomes negligible vs infrastructure

---

## System Design & Architecture

### Q6: Walk me through your system design process for this fraud resolution system.

**Answer:**

**System Design Methodology:**

I follow a **structured 7-step process** for system design:

```
1. Requirements Gathering
   ↓
2. Capacity Planning
   ↓
3. High-Level Architecture
   ↓
4. Component Design
   ↓
5. Data Model Design
   ↓
6. API Design
   ↓
7. Non-Functional Requirements (NFRs)
```

---

**STEP 1: Requirements Gathering**

**Functional Requirements:**

```
FR1: Customer Portal
  - Submit dispute (transaction_id, amount, reason)
  - View dispute status in real-time
  - Receive resolution notification

FR2: Agent Processing
  - Retrieve relevant policies (RAG)
  - Analyze transaction patterns
  - Assess fraud risk
  - Make resolution decision (approve/review/reject)

FR3: Analyst Dashboard
  - Review flagged cases
  - View agent rationale
  - Override decisions
  - Track metrics

FR4: Compliance
  - Audit trail for all decisions
  - Explainability (why was decision made?)
  - Policy versioning
```

**Non-Functional Requirements:**

```
NFR1: Performance
  - P99 latency: <5 seconds for decision
  - Throughput: 10,000 disputes/day
  - Availability: 99.9% uptime

NFR2: Scalability
  - Handle 10x traffic spikes (Black Friday)
  - Scale to 1M disputes/month

NFR3: Security
  - PCI-DSS compliant
  - Encrypted at rest and in transit
  - Role-based access control

NFR4: Cost
  - <$0.10 per dispute processed
  - Infrastructure <$1,000/month
```

---

**STEP 2: Capacity Planning**

**Traffic Estimation:**

```
Current Load:
- 50,000 disputes/month
- ~70 disputes/hour average
- Peak: 300 disputes/hour (5 QPS)

3-Year Projection:
- 1,000,000 disputes/month (20x growth)
- 1,400 disputes/hour average
- Peak: 6,000 disputes/hour (100 QPS)

Design Target: 150 QPS (50% headroom)
```

**Resource Calculation:**

```python
# Backend API
CPU per request: 100ms
Requests/sec: 150
CPU cores needed: 150 × 0.1 = 15 cores

With container overhead (20%): 18 cores
With redundancy (2x): 36 cores
With auto-scaling buffer: 10-50 cores (elastic)

# Memory
Per request: 50MB (agent execution)
Concurrent: 150 × 50MB = 7.5GB
With overhead: 10GB
Per pod: 2GB → 5 pods minimum

# Redis
Documents: 100,000 policies
Embedding size: 1536 dims × 4 bytes = 6KB each
Total vectors: 600MB
With metadata + session data: 2GB
With Redis overhead (3x): 6GB memory

# Decision: 
- Backend: t3.medium instances (2 vCPU, 4GB)
- Auto-scaling: 3-10 instances
- Redis: r6g.large (2 vCPU, 16GB memory)
```

---

**STEP 3: High-Level Architecture**

```
┌────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                         │
│  ┌──────────────┐              ┌──────────────────────┐        │
│  │   Customer   │              │  Analyst Dashboard   │        │
│  │   Portal     │              │    (Internal)        │        │
│  │  (React SPA) │              │   (React SPA)        │        │
│  └──────────────┘              └──────────────────────┘        │
│         │                                  │                    │
│         └──────────────────────────────────┘                    │
│                          │                                      │
│                   HTTPS (TLS 1.3)                              │
│                          ▼                                      │
├────────────────────────────────────────────────────────────────┤
│                  APPLICATION GATEWAY                           │
│         (AWS ALB + Cognito Auth + WAF)                         │
│                          │                                      │
├────────────────────────────────────────────────────────────────┤
│                     API LAYER                                  │
│         ┌─────────────────────────────┐                        │
│         │   FastAPI Backend (Python)  │                        │
│         │  - REST endpoints           │                        │
│         │  - SSE streaming            │                        │
│         │  - Rate limiting            │                        │
│         │  - Logging middleware       │                        │
│         └─────────────────────────────┘                        │
│                   │            │                                │
│        ┌──────────┘            └──────────┐                    │
│        ▼                                   ▼                    │
├────────────────────────────────────────────────────────────────┤
│   BUSINESS LOGIC LAYER           AGENT ORCHESTRATION           │
│  ┌──────────────────┐         ┌──────────────────────┐        │
│  │ Session Service  │         │  Orchestrator Agent  │        │
│  │ (Case Management)│         │   - RAG Agent        │        │
│  └──────────────────┘         │   - Transaction      │        │
│         │                     │   - Fraud Investigator│       │
│         │                     └──────────────────────┘        │
│         │                              │                       │
│         ▼                              ▼                       │
├────────────────────────────────────────────────────────────────┤
│                    DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ Redis Stack  │  │ AWS Bedrock  │  │  S3 (Policies)   │    │
│  │ - Sessions   │  │ - Nova Lite  │  │  - Documents     │    │
│  │ - Case data  │  │ - Claude     │  │  - Audit logs    │    │
│  │ - Vectors    │  │ - Titan Embed│  │                  │    │
│  └──────────────┘  └──────────────┘  └──────────────────┘    │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│                  OBSERVABILITY LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │   MLflow     │  │ CloudWatch   │  │  X-Ray Tracing   │    │
│  │  (Metrics)   │  │   (Logs)     │  │  (Performance)   │    │
│  └──────────────┘  └──────────────┘  └──────────────────┘    │
└────────────────────────────────────────────────────────────────┘
```

---

**STEP 4: Component Design**

**API Gateway Pattern:**

```
Why ALB + Cognito instead of API Gateway?

API Gateway:
✅ Built-in auth
✅ Rate limiting
❌ Cost: $3.50/million requests
❌ 29-second timeout (too short for agents)
❌ Limited WebSocket SSE

ALB + Cognito:
✅ Cost: $0.008/hour + $0.008/LCU (~$20/month)
✅ No timeout limits
✅ Native EKS integration
✅ Better for SSE streaming
✅ 98% cost reduction vs API Gateway
```

**Agent Orchestration Pattern:**

```
Pattern: Scatter-Gather

Orchestrator receives dispute
    │
    ├─> Dispatch to RAG Agent ──────┐
    │                                │
    ├─> Dispatch to Transaction ────┤  (Parallel execution)
    │                                │
    └─> Dispatch to Fraud ───────────┘
                 │
                 │ Wait for all (timeout: 10s)
                 ▼
          Gather responses
                 │
                 ▼
          Synthesize decision
                 │
                 ▼
          Return to client

Benefits:
- 3x faster than sequential (2s vs 6s)
- Resilient (continue if one agent fails)
- Observable (per-agent metrics)
```

---

**STEP 5: Data Model Design**

**Case Data (Redis JSON):**

```json
{
  "case_id": "uuid",
  "customer_id": "string",
  "transaction_id": "string",
  "dispute_amount_usd": "float",
  "dispute_reason": "string",
  "status": "PENDING | IN_REVIEW | RESOLVED",
  "created_at": "ISO8601",
  "agent_results": {
    "rag_response": {...},
    "transaction_analysis": {...},
    "fraud_assessment": {...}
  },
  "resolution": {
    "action": "APPROVE | REVIEW | REJECT",
    "risk_score": 0.85,
    "rationale": "string",
    "decided_at": "ISO8601"
  }
}
```

**Vector Index (Redis):**

```
Index: policy_index
Documents: 100,000 policy chunks

Schema:
- embedding: VECTOR[1536] FLOAT32 HNSW
- doc_id: TAG (policy document ID)
- policy_type: TAG (CHARGEBACK | FRAUD | REGULATION)
- chunk_text: TEXT (full-text search fallback)
- metadata: JSON (source, page, version)
```

---

**STEP 6: API Design**

**RESTful Endpoints:**

```
POST /api/v1/dispute
  Request:
    {
      "customer_id": "string",
      "transaction_id": "string",
      "dispute_amount_usd": 299.99,
      "dispute_reason": "Unauthorized charge"
    }
  
  Response: 202 Accepted
    {
      "case_id": "uuid",
      "status": "PENDING",
      "message": "Dispute submitted"
    }

GET /api/v1/dispute/{case_id}/stream
  Response: Server-Sent Events
    data: {"status": "PENDING", "progress": 0}
    data: {"status": "PROCESSING", "progress": 50, "step": "RAG_COMPLETE"}
    data: {"status": "RESOLVED", "progress": 100, "resolution": {...}}

GET /api/v1/dashboard/cases
  Query Params: ?status=IN_REVIEW&limit=50
  Response:
    {
      "cases": [...],
      "total": 150,
      "pagination": {...}
    }
```

---

**STEP 7: Non-Functional Requirements**

**Performance Targets:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Latency (P95) | <3s | CloudWatch |
| API Latency (P99) | <5s | CloudWatch |
| Agent Processing | <4s | MLflow |
| DB Query | <50ms | Redis INFO |

**Scalability Strategy:**

```
Horizontal Scaling:
- Backend: Kubernetes HPA (CPU >70%)
- Min replicas: 3
- Max replicas: 20
- Scale up: +2 pods when CPU >70% for 2 min
- Scale down: -1 pod when CPU <30% for 5 min

Load Balancing:
- ALB with round-robin
- Health checks every 30s
- Unhealthy threshold: 2 failures

Database:
- Redis: Vertical scaling (upgrade instance)
- Backup: Daily snapshots to S3
- Read replicas: 2 (for analytics)
```

**Security Design:**

```
Authentication:
┌──────────┐      ┌─────────┐      ┌─────────┐
│ Customer │─────>│ Cognito │─────>│   API   │
└──────────┘      └─────────┘      └─────────┘
     │                 │                 │
     │ Login           │ JWT Token       │ Validate
     │                 │                 │
     └─────────────────┴─────────────────┘

Authorization:
- Customer: Can only access own disputes
- Analyst: Can access all disputes + metrics
- Admin: Full access + configuration

Data Protection:
- TLS 1.3 in transit
- AES-256 at rest
- KMS for key management
- No plaintext secrets (AWS Secrets Manager)
```

---

**Design Trade-offs Made:**

| Decision | Alternative | Why Chosen |
|----------|-------------|------------|
| REST + SSE | GraphQL | Simpler, better caching |
| Redis | PostgreSQL + pgvector | 10x faster, multi-purpose |
| Bedrock | OpenAI API | 97% cheaper, compliance |
| EKS | EC2 | Auto-scaling, less ops |
| Monorepo | Separate repos | Easier versioning |

---

This comprehensive design process ensures we:
1. ✅ Meet all requirements
2. ✅ Scale efficiently
3. ✅ Optimize costs
4. ✅ Maintain simplicity
5. ✅ Enable future growth

---

## Scalability & Performance

### Q7: How do you design a scalable system? What specific techniques did you use?

**Answer:**

**Scalability Principles Applied:**

I use the **"Scale Cube" model** (X-axis, Y-axis, Z-axis scaling):

```
┌─────────────────────────────────────────────────────────────┐
│                    SCALE CUBE                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  X-Axis: Horizontal Duplication (Clones)                   │
│  ├─ Load balancer                                           │
│  ├─ Identical instances                                     │
│  └─ Stateless services                                      │
│                                                              │
│  Y-Axis: Functional Decomposition (Microservices)          │
│  ├─ Separate by function                                    │
│  ├─ Independent deployment                                  │
│  └─ Specialized optimization                                │
│                                                              │
│  Z-Axis: Data Partitioning (Sharding)                      │
│  ├─ Split by customer                                       │
│  ├─ Geographic regions                                      │
│  └─ Database sharding                                       │
└─────────────────────────────────────────────────────────────┘
```

**Our Implementation:**

---

**1. X-Axis Scaling: Horizontal Duplication**

**Stateless Backend Design:**

```python
# ❌ BAD: Stateful (doesn't scale)
class DisputeHandler:
    def __init__(self):
        self.active_cases = {}  # Instance-level state
    
    def process(self, dispute):
        self.active_cases[dispute.case_id] = dispute
        # Problem: State lost when pod restarts

# ✅ GOOD: Stateless (scales infinitely)
class DisputeHandler:
    def __init__(self, redis_client):
        self.redis = redis_client  # External state
    
    async def process(self, dispute):
        # Store in Redis, not memory
        await self.redis.json().set(
            f"case:{dispute.case_id}",
            "$",
            dispute.dict()
        )
        # Any pod can handle any request
```

**Auto-Scaling Configuration:**

```yaml
# Kubernetes Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3              # Always 3 for HA
  maxReplicas: 20             # Max during Black Friday
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Scale at 70% CPU
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80  # Scale at 80% memory
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60   # Wait 1 min
      policies:
      - type: Percent
        value: 50                      # Add 50% pods
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min
      policies:
      - type: Pods
        value: 1                       # Remove 1 pod
        periodSeconds: 60
```

**Load Testing Results:**

```
Test: Gradually increase load from 10 RPS to 200 RPS

Time    RPS    Pods   CPU%   Latency(P95)   Status
0:00    10     3      20%    800ms          ✓
0:05    50     3      55%    900ms          ✓
0:07    100    3      75%    1.2s           ✓ (Scaling triggered)
0:09    100    5      45%    950ms          ✓ (Pods added)
0:12    150    7      60%    1.0s           ✓
0:15    200    9      65%    1.1s           ✓
0:20    200    9      65%    1.1s           ✓ (Stable)

Conclusion:
- Linear scalability up to 200 RPS
- Auto-scaling responds in ~2 minutes
- P95 latency stays <1.5s under all loads
```

---

**2. Y-Axis Scaling: Functional Decomposition**

**Service Separation:**

```
┌──────────────────────────────────────────────────────────┐
│  Monolith (NOT scalable)                                 │
├──────────────────────────────────────────────────────────┤
│  Single service handles:                                 │
│  - Customer portal                                       │
│  - Analyst dashboard                                     │
│  - Agent processing                                      │
│  - Document ingestion                                    │
│                                                           │
│  Problem:                                                │
│  - Agent processing uses 90% CPU                         │
│  - But portal only needs 10% CPU                         │
│  - Must scale entire monolith                            │
│  - Wastes resources                                      │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Microservices (Scalable) ✅                             │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌───────────────┐  ┌────────────────┐                  │
│  │ API Service   │  │ Agent Service  │                  │
│  │ (Lightweight) │  │ (CPU-intensive)│                  │
│  │ 3-5 replicas  │  │ 5-20 replicas  │                  │
│  └───────────────┘  └────────────────┘                  │
│                                                           │
│  ┌───────────────┐  ┌────────────────┐                  │
│  │ Ingestion Svc │  │ Dashboard Svc  │                  │
│  │ (Batch jobs)  │  │ (Analytics)    │                  │
│  │ Cron schedule │  │ 2-3 replicas   │                  │
│  └───────────────┘  └────────────────┘                  │
│                                                           │
│  Benefits:                                               │
│  - Independent scaling per service                       │
│  - Resource optimization (right-size each)               │
│  - Deploy changes without affecting others               │
│  - Failure isolation                                     │
└──────────────────────────────────────────────────────────┘
```

**Our Current Architecture:**

We use **"modular monolith"** (pragmatic middle ground):

```
Single deployment, but logically separated:

backend/app/
├── api/           # HTTP layer (lightweight)
├── services/      # Business logic (moderate)
└── agents/        # AI processing (heavyweight)

Why not full microservices yet?
1. Complexity: 4 services = 4× deployment overhead
2. Team size: Small team (3-5 engineers)
3. Scale: Not at microservice scale yet (50K → 1M disputes)

When to split:
- When agent processing needs 10+ dedicated pods
- When deployment frequency differs significantly
- When team grows to 10+ engineers
```

---

**3. Z-Axis Scaling: Data Partitioning**

**Customer Sharding Strategy:**

```python
# Partition cases by customer_id hash

def get_shard(customer_id: str) -> int:
    """
    Deterministic sharding by customer_id.
    Ensures same customer always routes to same shard.
    """
    return int(hashlib.md5(customer_id.encode()).hexdigest(), 16) % NUM_SHARDS

# Redis key design includes shard
shard = get_shard(customer_id)
key = f"shard:{shard}:case:{case_id}"

# Benefits:
# 1. Distribute load across Redis instances
# 2. Scale storage horizontally
# 3. Isolate hot customers (prevent noisy neighbor)
```

**Geographic Partitioning:**

```
┌──────────────────────────────────────────────────────────┐
│           GLOBAL TRAFFIC ROUTING                         │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Customer Location ──> Route 53 (GeoDNS) ──> Region     │
│                                                           │
│  US East    ────────────────────> us-east-1              │
│  US West    ────────────────────> us-west-2              │
│  Europe     ────────────────────> eu-west-1              │
│                                                           │
│  Each region:                                            │
│  - Full backend deployment                               │
│  - Regional Redis cluster                                │
│  - Shared Bedrock (any region)                           │
│  - Replicated S3 (policy docs)                           │
│                                                           │
│  Benefits:                                               │
│  - <100ms latency worldwide                              │
│  - Regional failover                                     │
│  - Compliance (EU data stays in EU)                      │
└──────────────────────────────────────────────────────────┘
```

---

**4. Caching Strategy (Reduce Load)**

**Multi-Layer Cache:**

```
Request Flow with Caching:

1. Client Request
   ↓
2. CDN Cache (CloudFront)
   - Static assets: 24 hours
   - API responses: 0 (dynamic)
   ↓ (Cache MISS)
3. Application Cache (Redis)
   - Policy lookups: 1 hour
   - Transaction history: 5 minutes
   - Customer data: 10 minutes
   ↓ (Cache MISS)
4. Database (Redis primary)
   ↓
5. External API (Bedrock)
```

**Cache Implementation:**

```python
from functools import lru_cache
from cachetools import TTLCache
import redis.asyncio as redis

class CachedPolicyRetriever:
    def __init__(self, redis_client):
        self.redis = redis_client
        # In-memory cache (process-level)
        self.local_cache = TTLCache(maxsize=1000, ttl=300)  # 5 min
    
    async def get_policy(self, policy_id: str):
        # L1: In-memory cache (fastest, 0.1ms)
        if policy_id in self.local_cache:
            return self.local_cache[policy_id]
        
        # L2: Redis cache (fast, 1-5ms)
        cached = await self.redis.get(f"policy:{policy_id}")
        if cached:
            policy = json.loads(cached)
            self.local_cache[policy_id] = policy
            return policy
        
        # L3: Vector search + Bedrock (slow, 100-500ms)
        policy = await self._retrieve_from_vector_db(policy_id)
        
        # Populate caches
        await self.redis.setex(
            f"policy:{policy_id}",
            3600,  # 1 hour TTL
            json.dumps(policy)
        )
        self.local_cache[policy_id] = policy
        
        return policy

# Impact:
# - 90% requests hit L1 cache (0.1ms)
# - 9% requests hit L2 cache (2ms)
# - 1% requests hit L3 (500ms)
# - Average latency: 0.9×0.1 + 0.09×2 + 0.01×500 = 5.27ms
# - vs no cache: 500ms (95x improvement!)
```

---

**5. Asynchronous Processing (Decouple)**

**Background Jobs:**

```python
# ❌ Synchronous (blocks API response)
@router.post("/dispute")
async def submit_dispute(dispute: DisputeRequest):
    # Client waits for entire agent pipeline (4-6 seconds)
    result = await run_agents(dispute)  # SLOW
    return result

# ✅ Asynchronous (immediate response)
@router.post("/dispute")
async def submit_dispute(
    dispute: DisputeRequest,
    background_tasks: BackgroundTasks
):
    # Create case immediately
    case_id = await create_case(dispute)
    
    # Queue agent processing in background
    background_tasks.add_task(run_agents, dispute, case_id)
    
    # Return immediately (200ms)
    return {"case_id": case_id, "status": "PENDING"}

# Client polls /dispute/{case_id}/stream for updates
```

**Message Queue (Future Enhancement):**

```
Current: FastAPI BackgroundTasks (in-process)
Future: SQS + Lambda (distributed)

┌─────────────┐     ┌─────────┐     ┌──────────────┐
│  API Server │────>│   SQS   │────>│ Agent Lambda │
│ (Enqueue)   │     │ (Queue) │     │ (Process)    │
└─────────────┘     └─────────┘     └──────────────┘

Benefits:
- Retry failed jobs automatically
- Dead-letter queue for debugging
- Scale workers independently
- Better observability
```

---

**6. Database Optimization**

**Redis Tuning:**

```bash
# redis.conf optimizations

# 1. Memory
maxmemory 8gb
maxmemory-policy allkeys-lru  # Evict least-recently-used

# 2. Persistence (balance durability vs performance)
save ""                       # Disable RDB snapshots
appendonly yes               # Enable AOF
appendfsync everysec         # Fsync every second (good balance)

# 3. Networking
tcp-backlog 511
timeout 0
tcp-keepalive 300

# 4. Performance
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
