import base64
import json

from dash_extensions.streaming import sse_message


def yield_text_component(create_component_func, text_content):
    """Helper function to create a text component and yield it as an SSE message.

    Args:
        create_component_func: Function to create components (e.g., self.create_component)
        text_content: The text content to send

    Yields:
        SSE message with encoded component
    """
    component = create_component_func("text", text_content)
    encoded_delta = base64.b64encode(json.dumps(component.to_plotly_json()).encode("utf-8")).decode("utf-8")
    yield sse_message(encoded_delta)
