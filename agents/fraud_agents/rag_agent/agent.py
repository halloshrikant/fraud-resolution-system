# agents/rag_agent/agent.py
from agents import Agent, function_tool
from fraud_agents.extensions.litellm import LiteLLMModel
from fraud_agents.shared.litellm_client import router
from .retriever import PolicyRetriever

_llm = LiteLLMModel(model_id="nova-lite", router=router)
_retriever = PolicyRetriever()


@function_tool
def search_policy_knowledge_base(query: str, top_k: int = 5) -> str:
    """
    Perform semantic vector search in Redis to retrieve bank policy
    chunks most relevant to the given dispute query.
    Returns formatted policy excerpts with source citations.
    """
    results = _retriever.search(query=query, top_k=top_k)
    if not results:
        return "No relevant policy documents found."
    formatted = "\n\n".join(
        f"[Source: {r['doc_id']} | Policy: {r['policy_type']}]\n{r['chunk_text']}"
        for r in results
    )
    return formatted


rag_agent = Agent(
    name="RAGPolicyAgent",
    model=_llm,
    instructions="""
    You are a banking compliance policy retrieval specialist.
    Given a dispute description, use the search_policy_knowledge_base tool
    to find all relevant chargeback timelines, fraud thresholds, and regulatory
    rules that apply. Return a concise structured summary of applicable policies
    with exact source citations. Do not invent policy rules.
    """,
    tools=[search_policy_knowledge_base],
)