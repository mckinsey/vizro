"""Utility functions for the chat component."""

import json
import uuid

import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import dcc, html

from vizro_ai.models.chat._constants import CODE_BLOCK


def _parse_json_from_string(data_string: str) -> list[dict]:
    """Parse concatenated JSON objects from a string."""
    chunks = []
    buffer = ""
    brace_count = 0
    in_string = False
    escape_next = False

    for char in data_string:
        buffer += char

        # Track if we're inside a string to ignore braces there
        if not escape_next:
            if char == '"' and not in_string:
                in_string = True
            elif char == '"' and in_string:
                in_string = False
            elif char == "\\":
                escape_next = True
                continue
        else:
            escape_next = False
            continue

        # Count braces only outside of strings
        if not in_string:
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1

                # When brace count returns to 0, we have a complete JSON object
                if brace_count == 0 and buffer.strip():
                    try:
                        chunks.append(json.loads(buffer))
                        buffer = ""
                    except json.JSONDecodeError:
                        # If we can't parse it, keep accumulating
                        pass

    return chunks


def _parse_sse_chunks(animation_data) -> list[dict]:
    """Parse SSE animation data and return complete JSON objects.

    Args:
        animation_data: Raw SSE data from the streaming endpoint.

    Returns:
        List of parsed JSON objects from the SSE stream.
    """
    if not animation_data:
        return []

    try:
        if isinstance(animation_data, list):
            return [json.loads(msg) for msg in animation_data if msg]
        elif isinstance(animation_data, str):
            return _parse_json_from_string(animation_data)
        else:
            return [json.loads(animation_data)]
    except (json.JSONDecodeError, TypeError):
        return []


def _create_code_block_component(code_content, code_id, language="some-unsupported-lang") -> html.Div:
    """Create a consistent code block component with clipboard functionality.

    Args:
        code_content: The code content to display.
        code_id: Unique ID for the code block.
        language: Programming language for syntax highlighting. Defaults to "some-unsupported-lang".

    Returns:
        Dash HTML component with code block and clipboard button.
    """
    return html.Div(
        [
            dmc.CodeHighlight(
                code=code_content,
                id=code_id,
                language=language,
            ),
        ],
        style=CODE_BLOCK,
    )


def _flush_accumulated_text(current_text: str, content_items: list) -> str:
    """Helper to flush accumulated text to content_items.

    Args:
        current_text: The accumulated text content.
        content_items: List to append the text item to.

    Returns:
        Empty string after flushing, or original text if nothing to flush.
    """
    if current_text:
        content_items.append({"type": "text", "content": current_text})
        return ""
    return current_text


def _create_message_components(content, message_id):
    """Parse structured content and create components.

    Args:
        content: List of content items with type and content.
        message_id: Unique ID prefix for component IDs (can be message ID or component ID).

    Returns:
        List of Dash components or Dash HTML component containing the structured content.
    """
    components = []

    for item in content:
        item_type = item.get("type", "text")
        item_content = item.get("content", "")
        item_metadata = item.get("metadata", {})

        if item_type == "text" and item_content.strip():
            components.append(dcc.Markdown(item_content, className="markdown-container", style={"margin": 0}))
        elif item_type == "code":
            code_id = f"{message_id}-code-{uuid.uuid4()}"
            # Extract language from metadata with fallback to "some-unsupported-lang"
            # https://www.dash-mantine-components.com/components/code-highlight#supported-languages
            language = item_metadata.get("language", "some-unsupported-lang")
            components.append(_create_code_block_component(item_content, code_id, language))
            components.append(html.Br())
        elif item_type == "plotly_graph":
            fig_data = json.loads(item_content)
            components.append(
                dcc.Graph(
                    figure=go.Figure(fig_data),
                )
            )
            components.append(html.Br())

    return components
