"""Unit tests for VizroChatComponent."""

import json

import pytest
from dash import html
from vizro import Vizro

from vizro_chat.component import VizroChatComponent
from vizro_chat.processors import EchoProcessor


@pytest.fixture(autouse=True)
def reset_vizro():
    """Reset Vizro state before each test."""
    Vizro._reset()
    yield


def test_component_initialization():
    """Test basic component initialization."""
    component = VizroChatComponent(id="test-chat")
    assert component.id == "test-chat"
    assert component.input_placeholder == "Ask me a question..."
    assert component.button_text == "Send"
    assert isinstance(component.processor, EchoProcessor)


def test_build_method():
    """Test the build method creates correct UI structure."""
    component = VizroChatComponent(id="test-chat")
    result = component.build()

    assert isinstance(result, html.Div)

    # Check Store component
    store = result.children[0]
    assert store.id == "test-chat-messages"
    assert store.data == json.dumps([{"role": "assistant", "content": "Hello! How can I help you today?"}])

    # Check input and button existence
    input_group = result.children[1].children[1].children[0]
    assert len(input_group.children) == 2  # Textarea and Button
    assert input_group.children[0].id == "test-chat-input"
    assert input_group.children[1].id == "test-chat-submit"
