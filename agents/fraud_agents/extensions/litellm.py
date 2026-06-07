# fraud_agents/extensions/litellm.py
"""LiteLLM adapter for openai-agents SDK."""
from typing import Any, List, Optional
from collections.abc import AsyncIterator
from litellm import Router
from agents.models.interface import Model, ModelTracing
from agents.items import ModelResponse, TResponseInputItem, TResponseStreamEvent
from agents.model_settings import ModelSettings
from agents.tool import Tool
from agents.handoffs import Handoff
from agents.agent_output import AgentOutputSchemaBase
from openai.types.responses.response_prompt_param import ResponsePromptParam


class LiteLLMModel(Model):
    """
    LiteLLM adapter that implements openai-agents SDK Model interface.
    Routes requests through LiteLLM Router to AWS Bedrock models.
    """
    
    def __init__(self, model_id: str, router: Router):
        self.model_id = model_id
        self.router = router
    
    async def get_response(
        self,
        system_instructions: str | None,
        input: str | list[TResponseInputItem],
        model_settings: ModelSettings,
        tools: list[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: list[Handoff],
        tracing: ModelTracing,
        *,
        previous_response_id: str | None,
        conversation_id: str | None,
        prompt: ResponsePromptParam | None,
    ) -> ModelResponse:
        """
        Get a completion from LiteLLM router.
        Converts SDK format to LiteLLM and back to SDK response format.
        """
        # Build messages in OpenAI format
        messages = []
        if system_instructions:
            messages.append({"role": "system", "content": system_instructions})
        
        # Handle input (can be string or list of response items)
        if isinstance(input, str):
            messages.append({"role": "user", "content": input})
        else:
            # Convert SDK input items to messages
            for item in input:
                if hasattr(item, "role") and hasattr(item, "content"):
                    messages.append({"role": item.role, "content": item.content})
        
        # Call LiteLLM
        response = await self.router.acompletion(
            model=self.model_id,
            messages=messages,
            temperature=model_settings.temperature if hasattr(model_settings, "temperature") else 0.7,
            max_tokens=model_settings.max_tokens if hasattr(model_settings, "max_tokens") else 1024,
        )
        
        # Convert to SDK ModelResponse format
        # For simplicity, return a basic response structure
        # In production, you'd map all fields properly
        from agents.items import ModelResponse
        return ModelResponse(
            id=response.id,
            content=response.choices[0].message.content,
            role="assistant",
            model=self.model_id,
        )
    
    async def stream_response(
        self,
        system_instructions: str | None,
        input: str | list[TResponseInputItem],
        model_settings: ModelSettings,
        tools: list[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: list[Handoff],
        tracing: ModelTracing,
        *,
        previous_response_id: str | None,
        conversation_id: str | None,
        prompt: ResponsePromptParam | None,
    ) -> AsyncIterator[TResponseStreamEvent]:
        """
        Stream completions from LiteLLM router.
        """
        # Build messages (same as get_response)
        messages = []
        if system_instructions:
            messages.append({"role": "system", "content": system_instructions})
        
        if isinstance(input, str):
            messages.append({"role": "user", "content": input})
        else:
            for item in input:
                if hasattr(item, "role") and hasattr(item, "content"):
                    messages.append({"role": item.role, "content": item.content})
        
        # Stream from LiteLLM
        response = await self.router.acompletion(
            model=self.model_id,
            messages=messages,
            stream=True,
            temperature=model_settings.temperature if hasattr(model_settings, "temperature") else 0.7,
            max_tokens=model_settings.max_tokens if hasattr(model_settings, "max_tokens") else 1024,
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                # Yield SDK-compatible stream events
                yield chunk  # Simplified - in production, convert to proper SDK event type
