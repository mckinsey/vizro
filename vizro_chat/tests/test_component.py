"""Unit tests for chat component."""

import json
import pytest
from unittest.mock import Mock, patch
from dash import Dash
from dash.testing.application_runners import import_app
from vizro import Vizro
from vizro_chat import VizroChatComponent, EchoProcessor, OpenAIProcessor


@pytest.fixture
def vizro_app():
    """Create a test Vizro app."""
    app = Vizro()
    return app


@pytest.fixture
def chat_component(vizro_app):
    """Create a test chat component."""
    return VizroChatComponent(
        id="test-chat",
        vizro_app=vizro_app,
        processor=EchoProcessor()
    )


def test_component_initialization(chat_component):
    """Test component initialization."""
    assert chat_component.id == "test-chat"
    assert isinstance(chat_component.processor, EchoProcessor)
    assert chat_component.show_settings is True


def test_initial_messages(chat_component):
    """Test initial messages property."""
    messages = chat_component.messages
    assert len(messages) == 1
    assert messages[0]["role"] == "assistant"
    assert "Hello" in messages[0]["content"]


def test_build_structure(chat_component):
    """Test component build structure."""
    component = chat_component.build()
    
    # Check main structure
    assert component.type == "Div"
    
    # Check stores
    stores = [child for child in component.children if child.type == "Store"]
    assert len(stores) == 2
    assert all(store.id.startswith("test-chat-") for store in stores)
    assert all(store.storage_type == "session" for store in stores)


@pytest.mark.asyncio
async def test_streaming_route(chat_component):
    """Test streaming route functionality."""
    with patch("flask.request") as mock_request:
        mock_request.json = {
            "prompt": "test prompt",
            "chat_history": "[]",
            "api_settings": {"api_key": "test-key"}
        }
        
        # Get the streaming_chat function
        streaming_chat = None
        for route in chat_component.vizro_app.dash.server.url_map.iter_rules():
            if route.endpoint == f"streaming_chat_{chat_component.id}":
                streaming_chat = chat_component.vizro_app.dash.server.view_functions[route.endpoint]
                break
        
        assert streaming_chat is not None
        
        # Test the streaming response
        response = streaming_chat()
        assert response.mimetype == "text/event-stream"
        
        # Read the response stream
        chunks = []
        for chunk in response.response:
            chunks.append(chunk.decode())
        
        assert len(chunks) > 0
        assert "test prompt" in "".join(chunks)


def test_settings_callbacks(chat_component):
    """Test settings-related callbacks."""
    app = chat_component.vizro_app.dash
    
    # Test toggle settings callback
    toggle_settings = app.callback_map[f"{chat_component.id}-settings.is_open"]["callback"]
    assert toggle_settings(None) is False
    assert toggle_settings(1) is True
    
    # Test password visibility toggle callback
    toggle_visibility = app.callback_map[f"{chat_component.id}-api-key.type"]["callback"]
    key_type, base_type = toggle_visibility([1], [])  # Pass list values
    assert key_type == "text"
    assert base_type == "password"
    
    # Test toggle state update callback
    update_toggle = app.callback_map[f"{chat_component.id}-api-key-toggle.value"]["callback"]
    show_key, show_base = update_toggle("text", "password")
    assert show_key == [1]  # Expect list with value 1
    assert show_base == []  # Expect empty list
    
    # Test save settings callback
    save_settings = app.callback_map[f"{chat_component.id}-api-settings.data"]["callback"]
    settings = save_settings(1, "test-key", "test-base")
    assert settings == {"api_key": "test-key", "api_base": "test-base"}


def test_load_settings_callback(chat_component):
    """Test loading saved settings into inputs."""
    app = chat_component.vizro_app.dash
    
    # Test load settings callback
    load_settings = app.callback_map[f"{chat_component.id}-api-key.value"]["callback"]
    
    # When OffCanvas is closed or no settings
    assert load_settings(False, None) == ("", "")
    assert load_settings(False, {}) == ("", "")
    
    # When OffCanvas is opened with saved settings
    saved_settings = {"api_key": "test-key", "api_base": "test-base"}
    key, base = load_settings(True, saved_settings)
    assert key == "test-key"
    assert base == "test-base"


@pytest.mark.integration
def test_settings_persistence(dash_duo, vizro_app):
    """Test settings persistence across OffCanvas opens/closes."""
    component = VizroChatComponent(
        id="test-chat",
        vizro_app=vizro_app,
        processor=EchoProcessor()
    )
    
    app = Dash(__name__)
    app.layout = component.build()
    
    # Start the test
    dash_duo.start_server(app)
    
    # Open settings and enter values
    dash_duo.find_element("#test-chat-settings-icon").click()
    dash_duo.find_element("#test-chat-api-key").send_keys("test-key")
    dash_duo.find_element("#test-chat-api-base").send_keys("test-base")
    dash_duo.find_element("#test-chat-save-settings").click()
    
    # Close and reopen settings
    dash_duo.find_element("#test-chat-settings-icon").click()  # Close
    dash_duo.find_element("#test-chat-settings-icon").click()  # Reopen
    
    # Check if values are still there
    assert dash_duo.find_element("#test-chat-api-key").get_attribute("value") == "test-key"
    assert dash_duo.find_element("#test-chat-api-base").get_attribute("value") == "test-base"


@pytest.mark.integration
def test_component_integration(dash_duo, vizro_app):
    """Integration test for chat component."""
    component = VizroChatComponent(
        id="test-chat",
        vizro_app=vizro_app,
        processor=EchoProcessor()
    )
    
    app = Dash(__name__)
    app.layout = component.build()
    
    # Start the test
    dash_duo.start_server(app)
    
    # Test input and submit
    dash_duo.find_element("#test-chat-input").send_keys("test message")
    dash_duo.find_element("#test-chat-submit").click()
    
    # Check chat history
    history = dash_duo.find_element("#test-chat-history")
    assert "test message" in history.text
    
    # Test settings
    dash_duo.find_element("#test-chat-settings-icon").click()
    assert dash_duo.find_element("#test-chat-settings").is_displayed()


@pytest.mark.integration
def test_password_visibility_toggle(dash_duo, vizro_app):
    """Test password visibility toggle functionality."""
    component = VizroChatComponent(
        id="test-chat",
        vizro_app=vizro_app,
        processor=EchoProcessor()
    )
    
    app = Dash(__name__)
    app.layout = component.build()
    
    # Start the test
    dash_duo.start_server(app)
    
    # Open settings and enter values
    dash_duo.find_element("#test-chat-settings-icon").click()
    api_key_input = dash_duo.find_element("#test-chat-api-key")
    api_key_toggle = dash_duo.find_element("#test-chat-api-key-toggle")
    
    # Enter value
    api_key_input.send_keys("test-key")
    
    # Check initial state (password)
    assert api_key_input.get_attribute("type") == "password"
    
    # Toggle visibility
    api_key_toggle.click()
    assert api_key_input.get_attribute("type") == "text"
    assert api_key_input.get_attribute("value") == "test-key"
    
    # Toggle back
    api_key_toggle.click()
    assert api_key_input.get_attribute("type") == "password"
