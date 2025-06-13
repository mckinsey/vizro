"""Test script to verify the plugin pattern works correctly with VizroChatComponent."""

import vizro.models as vm
from vizro import Vizro
import vizro_ai.components as vcc

def test_plugin_pattern():
    """Test that the plugin pattern correctly registers routes."""
    
    # Create a chat component with EchoProcessor (no API key needed)
    chat_component = vcc.VizroChatComponent(
        id="test_chat",
        input_placeholder="Test message...",
        initial_message="Test chat initialized!",
        processor=vcc.EchoProcessor(),  # Simple processor for testing
    )
    
    # Register the component type with Vizro
    vm.Page.add_type("components", vcc.VizroChatComponent)
    
    # Create a simple page
    page = vm.Page(
        title="Test Chat Component",
        components=[chat_component],
    )
    
    # Create dashboard
    dashboard = vm.Dashboard(pages=[page])
    
    # Create Vizro app with the chat component as a plugin
    app = Vizro(plugins=[chat_component])
    app.build(dashboard)
    
    # Test that the route was registered
    expected_route = "/streaming-test_chat"
    routes = [rule.rule for rule in app.dash.server.url_map.iter_rules()]
    
    print("Registered routes:")
    for route in routes:
        print(f"  {route}")
    
    if expected_route in routes:
        print(f"✅ SUCCESS: Route {expected_route} was correctly registered!")
        return True
    else:
        print(f"❌ FAILURE: Route {expected_route} was not found in registered routes")
        return False

if __name__ == "__main__":
    success = test_plugin_pattern()
    exit(0 if success else 1) 