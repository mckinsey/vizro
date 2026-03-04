"""Tests for the vizro_dash_components.Markdown component."""

import time

import dash_mantine_components as dmc
from dash import Dash, html
from vizro_dash_components import Markdown


def test_markdown_renders(dash_duo):
    """Markdown component renders without errors."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(html.Div([Markdown("# Hello", id="markdown")]))
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#markdown h1", "Hello")
    assert dash_duo.get_logs() == []


def test_markdown_with_code(dash_duo):
    """Markdown component renders code blocks without errors."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(html.Div([Markdown("```python\nprint('hello')\n```", id="markdown")]))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#markdown pre")
    assert dash_duo.get_logs() == []


def test_markdown_with_mathjax(dash_duo):
    """Markdown component renders math with mathjax enabled."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(html.Div([Markdown("$E = mc^2$", mathjax=True, id="markdown")]))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#markdown")
    assert dash_duo.get_logs() == []


def test_markdown_link(dash_duo):
    """Markdown component renders links with target attribute."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Markdown(
                    "[example](https://example.com)",
                    link_target="_blank",
                    id="markdown",
                )
            ]
        )
    )
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#markdown a")
    link = dash_duo.find_element("#markdown a")
    assert link.get_attribute("target") == "_blank"
    assert dash_duo.get_logs() == []


def test_markdown_code_without_mantine_provider(dash_duo):
    """Markdown component with code block produces console errors when MantineProvider is missing."""
    app = Dash(__name__)
    app.layout = html.Div([Markdown("```python\nprint('hello')\n```", id="markdown")])
    dash_duo.start_server(app)
    # Give React time to attempt rendering and fail.
    time.sleep(3)
    logs = dash_duo.get_logs()
    assert any("MantineProvider was not found in component tree" in log["message"] for log in logs)
