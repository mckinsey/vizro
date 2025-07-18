"""Concrete implementation classes for chat processors."""

import time
from collections.abc import Generator
from typing import Optional

from vizro_ai.processors._base import (
    ChatMessage,
    ChatProcessor, 
    MessageType,
    _convert_structured_content_to_text,
    parse_markdown_stream,
)


class EchoProcessor(ChatProcessor):
    """Simple echo processor for testing and demonstration purposes."""

    def get_response(self, messages: list[dict], prompt: str) -> Generator[ChatMessage, None, None]:
        """Echo back the user's message with some processing.

        Args:
            messages: Previous conversation messages.
            prompt: Current user prompt.

        Yields:
            ChatMessage: Processed echo response messages.
        """
        try:
            # Simple streaming effect
            response = f"You said: {prompt}"
            for char in response:
                yield ChatMessage(type=MessageType.TEXT, content=char)
                time.sleep(0.02)  # Small delay for streaming effect

        except Exception:
            import logging

            logging.error("An error occurred in EchoProcessor:", exc_info=True)
            yield ChatMessage(type=MessageType.ERROR, content="An internal error has occurred.")


class OpenAIProcessor(ChatProcessor):
    """OpenAI processor for real LLM integration with streaming support."""

    def __init__(
        self,
        model: str = "gpt-4.1-nano",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ):
        """Initialize the OpenAI processor.

        Args:
            model (str): The OpenAI model to use. Defaults to `"gpt-4.1-nano"`.
            temperature (float): The temperature parameter for generation. Defaults to `0.7`.
            api_key (Optional[str]): Optional API key. If not provided, will look for
                OPENAI_API_KEY env var. Defaults to `None`.
            api_base (Optional[str]): Optional API base URL. Defaults to `None`.
        """
        try:
            from openai import OpenAI

            # Build client kwargs
            client_kwargs = {}
            if api_key:
                client_kwargs["api_key"] = api_key
            if api_base:
                client_kwargs["base_url"] = api_base

            self.client = OpenAI(**client_kwargs)
        except ImportError:
            raise ImportError("OpenAI package is required. Install it with: pip install openai")

        self.model = model
        self.temperature = temperature

    def get_response(self, messages: list[dict], prompt: str) -> Generator[ChatMessage, None, None]:
        """Get a streaming response from OpenAI.

        Args:
            messages: Previous conversation messages.
            prompt: Current user prompt.

        Yields:
            ChatMessage: Streaming response messages from OpenAI.
        """
        try:
            # Convert structured messages to plain text for OpenAI
            formatted_messages = [
                {"role": msg["role"], "content": _convert_structured_content_to_text(msg["content"])}
                for msg in messages
                if msg["role"] in ["user", "assistant"]
            ]
            formatted_messages.append({"role": "user", "content": prompt})

            # Get streaming response
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=self.temperature,
                stream=True,
            )

            # Convert token stream to ChatMessage stream
            token_generator = (chunk.choices[0].delta.content for chunk in stream if chunk.choices[0].delta.content)

            yield from parse_markdown_stream(token_generator)

        except Exception:
            yield ChatMessage(type=MessageType.ERROR, content="An internal error has occurred.")


class GraphProcessor(ChatProcessor):
    """Processor that demonstrates rendering charts with sample visualizations."""

    def get_response(self, messages: list[dict], prompt: str) -> Generator[ChatMessage, None, None]:
        """Generate a response with text and a sample chart.

        Args:
            messages: Previous conversation messages.
            prompt: Current user prompt.

        Yields:
            ChatMessage: Response messages including sample chart visualization.
        """
        try:
            import vizro.plotly.express as px

            response = f"Here's a chart based on your request: '{prompt}'\n\n"
            for char in response:
                yield ChatMessage(type=MessageType.TEXT, content=char)

            code = (
                "import plotly.express as px\n\n"
                "fig = px.scatter(px.data.iris(), x='sepal_width', "
                "y='sepal_length', color='species')"
            )
            yield ChatMessage(type=MessageType.CODE, content=code, metadata={"language": "python"})

            yield ChatMessage(type=MessageType.TEXT, content="\n\nHere's the chart:\n\n")

            fig = px.scatter(
                px.data.iris(),
                x="sepal_width",
                y="sepal_length",
                color="species",
                title="Sample Iris Dataset Visualization",
                template="vizro_dark",
            )

            yield ChatMessage(
                type=MessageType.PLOTLY_GRAPH,
                content=fig.to_json(),
            )

        except Exception:
            import logging

            logging.error("An error occurred in GraphProcessor:", exc_info=True)
            yield ChatMessage(type=MessageType.ERROR, content="An internal error has occurred.") 