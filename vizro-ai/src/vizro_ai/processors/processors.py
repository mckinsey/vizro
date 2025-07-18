"""Captured callable functions for chat processors."""

from typing import Optional

from vizro.models.types import capture
from vizro_ai.processors._implementations import EchoProcessor, GraphProcessor, OpenAIProcessor


@capture("processor")
def echo_processor() -> EchoProcessor:
    """Create an EchoProcessor instance.
    
    Returns:
        EchoProcessor: Echo processor that repeats user input.
    """
    return EchoProcessor()


@capture("processor")
def openai_processor(
    model: str = "gpt-4.1-nano",
    temperature: float = 0.7,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
) -> OpenAIProcessor:
    """Create an OpenAIProcessor instance.
    
    Args:
        model: The OpenAI model to use. Defaults to "gpt-4.1-nano".
        temperature: The temperature parameter for generation. Defaults to 0.7.
        api_key: Optional API key. If not provided, will look for OPENAI_API_KEY env var.
        api_base: Optional API base URL.
        
    Returns:
        OpenAIProcessor: OpenAI processor instance.
    """
    return OpenAIProcessor(
        model=model,
        temperature=temperature,
        api_key=api_key,
        api_base=api_base,
    )


@capture("processor")
def graph_processor() -> GraphProcessor:
    """Create a GraphProcessor instance.
    
    Returns:
        GraphProcessor: Graph processor that demonstrates chart rendering.
    """
    return GraphProcessor() 