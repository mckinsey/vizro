"""Unit tests for chat processors."""

import os
from unittest.mock import MagicMock, patch, Mock

import pytest

from vizro_chat.processors import EchoProcessor, OpenAIProcessor


def test_echo_processor():
    """Test EchoProcessor functionality."""
    processor = EchoProcessor()
    messages = [{"role": "user", "content": "test"}]
    response = list(processor.get_response(messages, "Hello"))
    
    assert len(response) == 10
    assert all("Hello" in msg for msg in response)
    assert all("Echo" in msg for msg in response)


def test_echo_processor_none_input():
    """Test EchoProcessor with None inputs."""
    processor = EchoProcessor()
    response = list(processor.get_response(None, None))
    assert len(response) == 1
    assert "Error" in response[0]


# Skip OpenAI tests if the package isn't installed
openai_not_installed = False
try:
    from vizro_chat.processors import OpenAIProcessor
except ImportError:
    openai_not_installed = True

pytestmark = pytest.mark.skipif(openai_not_installed, reason="OpenAI package not installed")


@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    with patch("vizro_chat.processors.OpenAI") as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        yield mock_client


@pytest.mark.skipif(openai_not_installed, reason="OpenAI package not installed")
def test_openai_processor_init(mock_openai):
    """Test OpenAIProcessor initialization."""
    processor = OpenAIProcessor(model="test-model", temperature=0.5)
    assert processor.model == "test-model"
    assert processor.temperature == 0.5
    assert processor.client is None


def test_openai_processor_initialize_client(mock_openai):
    """Test OpenAIProcessor client initialization."""
    processor = OpenAIProcessor()
    processor.initialize_client(api_key="test-key", api_base="test-base")
    
    mock_openai.assert_called_once_with(api_key="test-key", base_url="test-base")


def test_openai_processor_get_response(mock_openai):
    """Test OpenAIProcessor response generation."""
    # Mock the streaming response
    mock_chunk = Mock()
    mock_chunk.choices = [Mock()]
    mock_chunk.choices[0].delta.content = "test response"
    
    mock_openai.chat.completions.create.return_value = [mock_chunk]
    
    processor = OpenAIProcessor()
    processor.initialize_client(api_key="test-key")
    
    messages = [{"role": "user", "content": "test"}]
    response = list(processor.get_response(messages, "Hello"))
    
    assert response == ["test response"]
    mock_openai.chat.completions.create.assert_called_once_with(
        model="gpt-4o-mini",
        messages=[*messages, {"role": "user", "content": "Hello"}],
        temperature=1.0,
        stream=True,
    )


def test_openai_processor_error_handling(mock_openai):
    """Test OpenAIProcessor error handling."""
    mock_openai.chat.completions.create.side_effect = Exception("API Error")
    
    processor = OpenAIProcessor()
    processor.initialize_client(api_key="test-key")
    
    response = list(processor.get_response([], "test"))
    assert len(response) == 1
    assert "Error" in response[0]


def test_openai_processor_import_error():
    """Test OpenAIProcessor handles missing openai package."""
    with patch.dict("sys.modules", {"openai": None}):
        with pytest.raises(ImportError, match="OpenAI package not installed"):
            OpenAIProcessor()
