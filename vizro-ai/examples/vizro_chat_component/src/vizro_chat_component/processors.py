"""Chat processors for generating responses to user prompts."""

import os
from abc import ABC, abstractmethod
from collections.abc import Iterator
from time import sleep
from typing import Optional, Generator, List
import re
import json

# Try to import OpenAI, but make it optional
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class ChatProcessor(ABC):
    """Abstract base class for chat processors."""

    @abstractmethod
    def get_response(self, messages: List[dict], prompt: str) -> Generator[str, None, None]:
        """Get a response from the chat processor."""
        pass


def stream_structured_markdown(token_stream):
    buffer = ""
    in_code_block = False
    code_block_lang = ""
    code_block_delim = "```"

    for token in token_stream:
        buffer += token

        # Handle code blocks
        while code_block_delim in buffer:
            before, after = buffer.split(code_block_delim, 1)
            if in_code_block:
                # End of code block
                yield json.dumps({
                    "type": "code",
                    "content": before,
                    "language": code_block_lang
                })
                in_code_block = False
                code_block_lang = ""
            else:
                # Start of code block, check for language
                lines = after.splitlines()
                if lines and re.match(r"^\w+$", lines[0]):
                    code_block_lang = lines[0]
                    after = "\n".join(lines[1:])
                else:
                    code_block_lang = ""
                if before:
                    yield json.dumps({"type": "text", "content": before})
                in_code_block = True
            buffer = after

        # Only yield full buffer at the end, do not split or strip

    # Yield any remaining buffer at the end
    if buffer:
        if in_code_block:
            yield json.dumps({"type": "code", "content": f"```{buffer}```\n\n", "language": code_block_lang})
        else:
            yield json.dumps({"type": "text", "content": f"{buffer}\n\n"})


class EchoProcessor(ChatProcessor):
    """Simple echo processor that repeats the user's message."""

    def get_response(self, messages: List[dict], prompt: str) -> Generator[str, None, None]:
        """Echo the user's message back 10 times as structured JSON."""
        try:
            if messages is None or prompt is None:
                raise ValueError("Messages and prompt cannot be None")

            for i in range(10):
                sleep(1)
                yield json.dumps({"type": "text", "content": f"Echo {i + 1}: {prompt}"})
        except Exception as e:
            yield json.dumps({"type": "error", "content": f"Error in EchoProcessor: {e!s}"})


class OpenAIProcessor(ChatProcessor):
    """Processor that uses OpenAI API to generate responses."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ):
        """Initialize the OpenAI processor.

        Args:
            model: The OpenAI model to use
            temperature: The temperature parameter for generation
            api_key: Optional API key. If not provided, will look for OPENAI_API_KEY env var
            api_base: Optional API base URL
        """
        self.model = model
        self.temperature = temperature
        self._api_key = api_key
        self._api_base = api_base
        self.client = None
        self.initialize_client(api_key, api_base)

    def initialize_client(self, api_key: Optional[str] = None, api_base: Optional[str] = None) -> None:
        """Initialize or reinitialize the OpenAI client with new credentials."""
        if api_key:
            self._api_key = api_key
        if api_base:
            self._api_base = api_base

        # Only create client if we have an API key
        if self._api_key:
            kwargs = {"api_key": self._api_key}
            if self._api_base:
                kwargs["base_url"] = self._api_base
            self.client = OpenAI(**kwargs)

    def get_response(self, messages: List[dict], prompt: str) -> Generator[str, None, None]:
        """Get a streaming response from OpenAI as structured JSON."""
        if not self.client:
            yield json.dumps({"type": "error", "content": "Please set up your OpenAI API key in the settings panel (key icon) to use this feature."})
            return

        try:
            formatted_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
                if msg["role"] in ["user", "assistant"]
            ]
            formatted_messages.append({"role": "user", "content": prompt})

            stream = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=self.temperature,
                stream=True,
            )

            # Use the structured markdown streamer
            yield from stream_structured_markdown(
                (chunk.choices[0].delta.content for chunk in stream if chunk.choices[0].delta.content)
            )

        except Exception as e:
            error_message = str(e)
            yield json.dumps({"type": "error", "content": error_message})
