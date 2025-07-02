"""Chat processors for generating responses to user prompts."""

import re
import time
from abc import ABC, abstractmethod
from collections.abc import Generator
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


def _convert_structured_content_to_text(content: Union[str, list[dict[str, Any]]]) -> str:
    """Convert structured content back to plain text/markdown format for LLM consumption.

    Args:
        content: Either a plain string or structured content list.

    Returns:
        Plain text/markdown string suitable for LLM.
    """
    if isinstance(content, str):
        return content

    if not isinstance(content, list):
        return str(content)

    result_parts = []

    for item in content:
        if not isinstance(item, dict):
            result_parts.append(str(item))
            continue

        item_type = item.get("type", "text")
        item_content = item.get("content", "")
        item_metadata = item.get("metadata", {})

        if item_type == "text":
            result_parts.append(item_content)
        elif item_type == "code":
            language = item_metadata.get("language", "")
            if language:
                result_parts.append(f"```{language}\n{item_content}\n```")
            else:
                result_parts.append(f"```\n{item_content}\n```")
        elif item_type == "plotly_graph":
            # For plotly graphs, just mention that a graph was shown
            result_parts.append("[A Plotly graph was displayed here]")
        elif item_type == "error":
            result_parts.append(f"Error: {item_content}")
        else:
            # Unknown type, just include the content
            result_parts.append(item_content)

    return "".join(result_parts)


class MessageType(str, Enum):
    """Supported message types for chat responses."""

    TEXT = "text"
    CODE = "code"
    ERROR = "error"
    PLOTLY_GRAPH = "plotly_graph"


class ChatMessage(BaseModel):
    """Standardized chat message schema.

    Args:
        type (MessageType): Type of the message content. Defaults to `MessageType.TEXT`.
        content (str): The actual message content.
        metadata (dict[str, Any]): Optional metadata for the message. Defaults to `{}`.
    """

    type: MessageType = Field(default=MessageType.TEXT, description="Type of the message content")
    content: str = Field(description="The actual message content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Optional metadata for the message")

    def to_json(self) -> str:
        """Convert message to JSON string for streaming."""
        return self.model_dump_json()


class ChatProcessor(ABC):
    """Abstract base class for chat processors that generate responses to user prompts."""

    @abstractmethod
    def get_response(self, messages: list[dict], prompt: str) -> Generator[ChatMessage, None, None]:
        """Get a response from the chat processor.

        Args:
            messages: Previous conversation messages.
            prompt: Current user prompt.

        Yields:
            ChatMessage: Structured messages to be rendered.
        """
        pass

    @property
    def supports_streaming(self) -> bool:
        """Whether this processor supports streaming responses.

        Returns:
            Whether streaming is supported.
        """
        return True


def parse_markdown_stream(token_stream: Generator[str, None, None]) -> Generator[ChatMessage, None, None]:
    """Parse a stream of tokens and yield structured messages based on markdown patterns.

    Args:
        token_stream: Generator of string tokens from an LLM.

    Yields:
        ChatMessage: Structured messages for text and code blocks.
    """
    buffer = ""
    in_code_block = False
    code_language = ""

    for token in token_stream:
        buffer += token

        if not in_code_block and "```" in buffer:
            # Starting a code block
            before, delimiter, after = buffer.partition("```")

            # Yield any text before the code block
            if before:
                yield ChatMessage(type=MessageType.TEXT, content=before)

            # Extract language if present
            lines = after.split("\n", 1)
            if lines and lines[0].strip() and re.match(r"^\w+$", lines[0].strip()):
                code_language = lines[0].strip()
                buffer = lines[1] if len(lines) > 1 else ""
            else:
                code_language = ""
                buffer = after

            in_code_block = True

        elif in_code_block and "```" in buffer:
            # Ending a code block
            code_content, delimiter, after = buffer.partition("```")

            if code_content.strip():
                yield ChatMessage(
                    type=MessageType.CODE, content=code_content.strip(), metadata={"language": code_language}
                )

            buffer = after
            in_code_block = False
            code_language = ""

        elif not in_code_block:
            # Regular text - yield immediately for streaming effect
            yield ChatMessage(type=MessageType.TEXT, content=token)
            buffer = ""

    # Handle remaining buffer
    if buffer.strip():
        if in_code_block:
            yield ChatMessage(type=MessageType.CODE, content=buffer.strip(), metadata={"language": code_language})
        else:
            yield ChatMessage(type=MessageType.TEXT, content=buffer)


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
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ):
        """Initialize the OpenAI processor.

        Args:
            model (str): The OpenAI model to use. Defaults to `"gpt-4o-mini"`.
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
            import logging

            logging.error("An error occurred in OpenAIProcessor:", exc_info=True)
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
