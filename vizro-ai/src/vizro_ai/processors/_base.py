"""Chat processors base classes and utilities."""

import re
from abc import ABC, abstractmethod
from collections.abc import Generator
from enum import Enum
from typing import Any, Union

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
