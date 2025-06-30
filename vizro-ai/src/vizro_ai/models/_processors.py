"""Chat processors for generating responses to user prompts."""

import re
from abc import ABC, abstractmethod
from enum import Enum
import time
from typing import Any, Dict, Generator, List, Optional

from pydantic import BaseModel, Field



class MessageType(str, Enum):
    """Supported message types for chat responses."""
    TEXT = "text"
    CODE = "code"
    ERROR = "error"
    PLOTLY_GRAPH = "plotly_graph"


class ChatMessage(BaseModel):
    """Standardized chat message schema."""
    type: MessageType = Field(default=MessageType.TEXT, description="Type of the message content")
    content: str = Field(description="The actual message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata for the message")
    
    def to_json(self) -> str:
        """Convert message to JSON string for streaming."""
        return self.model_dump_json()


class ChatProcessor(ABC):
    """Abstract base class for chat processors."""

    @abstractmethod
    def get_response(self, messages: List[dict], prompt: str) -> Generator[ChatMessage, None, None]:
        """Get a response from the chat processor.
        
        Args:
            messages: Previous conversation messages
            prompt: Current user prompt
            
        Yields:
            ChatMessage: Structured messages to be rendered
        """
        pass
    
    @property
    def supports_streaming(self) -> bool:
        """Whether this processor supports streaming responses."""
        return True


def parse_markdown_stream(token_stream: Generator[str, None, None]) -> Generator[ChatMessage, None, None]:
    """Parse a stream of tokens and yield structured messages based on markdown patterns.
    
    Args:
        token_stream: Generator of string tokens from an LLM
        
    Yields:
        ChatMessage: Structured messages for text and code blocks
    """
    buffer = ""
    in_code_block = False
    code_language = ""
    
    for token in token_stream:
        if in_code_block:
            # In code block, buffer until we find the closing delimiter
            buffer += token
            
            # Check if we have the closing delimiter
            if "```" in buffer:
                before, delimiter, after = buffer.partition("```")
                # Extract the actual code content (remove the delimiter)
                code_content = before
                if code_content:
                    yield ChatMessage(
                        type=MessageType.CODE,
                        content=code_content,
                        metadata={"language": code_language}
                    )
                in_code_block = False
                code_language = ""
                buffer = after
        else:
            # Not in code block - check for opening delimiter
            buffer += token
            
            # Check for code block start
            if "```" in buffer:
                before, delimiter, after = buffer.partition("```")
                
                # Yield any text before the code block
                if before:
                    yield ChatMessage(type=MessageType.TEXT, content=before)
                
                # Extract language from the next portion
                lines = after.split('\n', 1)
                if lines and re.match(r"^\w+$", lines[0].strip()):
                    code_language = lines[0].strip()
                    buffer = lines[1] if len(lines) > 1 else ""
                else:
                    code_language = ""
                    buffer = after
                
                in_code_block = True
            else:
                # No code block delimiter - yield the token immediately for streaming
                yield ChatMessage(type=MessageType.TEXT, content=token)
                buffer = ""  # Clear buffer since we yielded the content
    
    # Handle remaining buffer
    if buffer:
        if in_code_block:
            # Incomplete code block
            yield ChatMessage(
                type=MessageType.CODE,
                content=buffer,
                metadata={"language": code_language}
            )
        elif buffer.strip():
            # Remaining text
            yield ChatMessage(type=MessageType.TEXT, content=buffer)


class EchoProcessor(ChatProcessor):
    """Simple echo processor for testing purposes."""

    def get_response(self, messages: List[dict], prompt: str) -> Generator[ChatMessage, None, None]:
        """Echo the user's message back with simulated streaming."""
        try:
            if not prompt:
                raise ValueError("Prompt cannot be empty")

            # Simulate streaming by yielding the prompt character by character
            for char in f"You said: {prompt}":
                yield ChatMessage(type=MessageType.TEXT, content=char)
                
            # Add a final newline
            yield ChatMessage(type=MessageType.TEXT, content="\n")
            
        except Exception as e:
            yield ChatMessage(
                type=MessageType.ERROR,
                content=f"Error in EchoProcessor: {e!s}"
            )


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
        # Import OpenAI only when needed
        try:
            from openai import OpenAI
            self._OpenAI = OpenAI
        except ImportError:
            raise ImportError("OpenAI package is required for OpenAIProcessor. Install it with: pip install openai")
        
        self.model = model
        self.temperature = temperature
        self._api_key = api_key
        self._api_base = api_base
        self.client = None
        self.initialize_client(api_key, api_base)
        
        if not self.client:
            raise ValueError("OpenAI API key is required and was not provided or is invalid.")

    def initialize_client(self, api_key: Optional[str] = None, api_base: Optional[str] = None) -> None:
        """Initialize or reinitialize the OpenAI client with new credentials."""
        if api_key:
            self._api_key = api_key
        if api_base:
            self._api_base = api_base

        if self._api_key:
            kwargs = {"api_key": self._api_key}
            if self._api_base:
                kwargs["base_url"] = self._api_base
            self.client = self._OpenAI(**kwargs)

    def get_response(self, messages: List[dict], prompt: str) -> Generator[ChatMessage, None, None]:
        """Get a streaming response from OpenAI."""
        try:
            formatted_messages = [
                {"role": msg["role"], "content": msg["content"]}
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
            token_generator = (
                chunk.choices[0].delta.content 
                for chunk in stream 
                if chunk.choices[0].delta.content
            )
            
            yield from parse_markdown_stream(token_generator)

        except Exception as e:
            yield ChatMessage(
                type=MessageType.ERROR,
                content=f"Error in OpenAI Processor: {e!s}"
            )



class GraphProcessor(ChatProcessor):
    """Simple processor that demonstrates rendering different content types including Plotly graphs."""

    def get_response(self, messages: List[dict], prompt: str) -> Generator[ChatMessage, None, None]:
        """Generate a response with text, code, and a sample Plotly graph."""
        try:
            import vizro.plotly.express as px
            
            for char in f"You said: {prompt}\n\n":
                yield ChatMessage(type=MessageType.TEXT, content=char)
                
            for char in "I'm a bot that always responds with a plotly graph:\n\n":
                yield ChatMessage(type=MessageType.TEXT, content=char)
            
            sample_code = "import plotly.express as px\ndf = px.data.iris()\nfig = px.scatter(df, x='sepal_width', y='sepal_length', color='species')"
            yield ChatMessage(
                type=MessageType.CODE, 
                content=sample_code,
                metadata={"language": "python"}
            )
            
            for char in "\nHere's a sample interactive chart:\n\n":
                yield ChatMessage(type=MessageType.TEXT, content=char)

            fig = px.scatter(
                px.data.iris(), 
                x='sepal_width', 
                y='sepal_length', 
                color='species',
            )
            
            time.sleep(1)
            yield ChatMessage(
                type=MessageType.PLOTLY_GRAPH,
                content=fig.to_json(),
            )
            
            time.sleep(2)
            for char in "\nThis demonstrates mixed content rendering in the chat interface. Now let's try a different theme:":
                yield ChatMessage(type=MessageType.TEXT, content=char)

            fig2 = px.scatter(
                px.data.iris(), 
                x='sepal_width', 
                y='sepal_length', 
                color='species',
                template="vizro_dark",
            )

            time.sleep(5)
            yield ChatMessage(
                type=MessageType.PLOTLY_GRAPH,
                content=fig2.to_json(),
            )
                
        except Exception as e:
            yield ChatMessage(
                type=MessageType.ERROR,
                content=f"Error in GraphProcessor: {e!s}"
            ) 