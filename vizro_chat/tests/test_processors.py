"""Unit tests for chat processors."""

import os
from unittest.mock import MagicMock, patch

import pytest

from vizro_chat.processors import ChatProcessor, EchoProcessor


def test_echo_processor():
    """Test EchoProcessor functionality."""
    processor = EchoProcessor()
    messages = []
    prompt = "Hello, world!"
    
    response = list(processor.get_response(messages, prompt))
    assert len(response) == 10
    assert all(isinstance(msg, str) for msg in response)
    assert all("Hello, world!" in msg for msg in response)


def test_echo_processor_error_handling():
    """Test EchoProcessor error handling."""
    processor = EchoProcessor()
    
    # Simulate an error by passing invalid types
    response = list(processor.get_response(None, None))  # type: ignore
    assert len(response) == 1
    assert "Error in EchoProcessor" in response[0]


# Skip OpenAI tests if the package isn't installed
openai_not_installed = False
try:
    from vizro_chat.processors import OpenAIProcessor
except ImportError:
    openai_not_installed = True

pytestmark = pytest.mark.skipif(
    openai_not_installed,
    reason="OpenAI package not installed"
)


@pytest.fixture
def mock_openai():
    """Create a mock OpenAI client."""
    with patch("openai.OpenAI") as mock_client:
        yield mock_client


@pytest.mark.skipif(openai_not_installed, reason="OpenAI package not installed")
def test_openai_processor_initialization(mock_openai):
    """Test OpenAIProcessor initialization."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_BASE_URL": "test-url"}):
        processor = OpenAIProcessor()
        assert processor.model == "gpt-4o-mini"
        assert processor.temperature == 1.0
        mock_openai.assert_called_once()


def test_openai_processor_response(mock_openai):
    """Test OpenAIProcessor response generation."""
    mock_instance = MagicMock()
    mock_openai.return_value = mock_instance
    
    # Mock the streaming response
    mock_chunk = MagicMock()
    mock_chunk.choices[0].delta.content = "test response"
    mock_instance.chat.completions.create.return_value = [mock_chunk]
    
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_BASE_URL": "test-url"}):
        processor = OpenAIProcessor()
        messages = []
        prompt = "test prompt"
        
        response = list(processor.get_response(messages, prompt))
        assert response == ["test response"]
        
        # Verify API call
        mock_instance.chat.completions.create.assert_called_once_with(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test prompt"}],
            temperature=1.0,
            stream=True,
        )


def test_openai_processor_error_handling(mock_openai):
    """Test OpenAIProcessor error handling."""
    mock_instance = MagicMock()
    mock_openai.return_value = mock_instance
    
    # Simulate different types of errors
    error_cases = [
        ("Token is inactive due to expiration", "Error: OpenAI API token has expired"),
        ("PermissionDenied", "Error: Permission denied"),
        ("RateLimitExceeded", "Error: Rate limit exceeded"),
        ("Unknown error", "Error: Unknown error"),
    ]
    
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_BASE_URL": "test-url"}):
        processor = OpenAIProcessor()
        
        for error_msg, expected_response in error_cases:
            mock_instance.chat.completions.create.side_effect = Exception(error_msg)
            response = list(processor.get_response([], "test"))
            assert len(response) == 1
            assert expected_response in response[0]


def test_openai_processor_import_error():
    """Test OpenAIProcessor handles missing openai package."""
    with patch.dict("sys.modules", {"openai": None}):
        with pytest.raises(ImportError, match="OpenAI package not installed"):
            OpenAIProcessor() 