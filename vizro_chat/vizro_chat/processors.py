"""Chat processors for generating responses to user prompts."""

import os
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path


class ChatProcessor(ABC):
    """Abstract base class for chat processors."""

    @abstractmethod
    def get_response(self, messages: list[dict[str, str]], user_prompt: str) -> Iterator[str]:
        """Generate response chunks for the given messages and prompt."""
        pass


class EchoProcessor(ChatProcessor):
    """Simple echo processor that repeats the user's message."""

    def get_response(self, messages: list[dict[str, str]], user_prompt: str) -> Iterator[str]:
        """Echo the user's message back 10 times."""
        try:
            for i in range(10):
                yield f"Echo {i + 1}: {user_prompt}\n"
        except Exception as e:
            yield f"Error in EchoProcessor: {e!s}"


class OpenAIProcessor(ChatProcessor):
    """OpenAI chat processor."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 1.0):
        """Initialize OpenAI chat processor."""
        try:
            from openai import OpenAI

            env_path = Path(__file__).parent.parent.parent / "vizro-core" / "examples" / "dev_1" / ".env"
            if env_path.exists():
                from dotenv import load_dotenv

                load_dotenv(env_path)

            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))
            self.model = model
            self.temperature = temperature
        except ImportError:
            raise ImportError("OpenAI package not installed. Install with 'pip install openai'")

    def get_response(self, messages: list[dict[str, str]], user_prompt: str) -> Iterator[str]:
        """Generate streaming response using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[*messages, {"role": "user", "content": user_prompt}],
                temperature=self.temperature,
                stream=True,
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            error_message = str(e)
            if "Token is inactive" in error_message:
                yield "Error: OpenAI API token has expired. Please update your token."
            elif "PermissionDenied" in error_message:
                yield "Error: Permission denied. Please check your API token and permissions."
            elif "RateLimitExceeded" in error_message:
                yield "Error: Rate limit exceeded. Please try again later."
            else:
                yield f"Error: {error_message}"
