"""Test usage of vizro_dash_components.Markdown with all features."""

import dash
import vizro_dash_components
from dash import Input, Output, clientside_callback, html

app = dash.Dash(__name__)

markdown_content = """
# Hello Vizro Markdown

This is a test of the **vizro_dash_components.Markdown** component.

## Features

- Full markdown support
- Code highlighting with copy button
- LaTeX math support
- HTML parsing with custom components

## Code Example

Here's a Python code block with syntax highlighting:

```python
def greet(name: str) -> str:
    \"\"\"Return a greeting message.\"\"\"
    return f"Hello, {name}!"

# Usage
message = greet("World")
print(message)
```

And some JavaScript:

```javascript
const add = (a, b) => a + b;
console.log(add(2, 3));
```

## Inline Code

You can also use `inline code` in your markdown.

## Links

Here's a [link to Google](https://www.google.com) that should open in a new tab.
"""

markdown_with_math = """
## Math Support

When `mathjax=True`, you can render LaTeX math:

Inline math: $E = mc^2$

Block math:

$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

The quadratic formula: $x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$
"""

markdown_with_html = """
## HTML Support

When `dangerously_allow_html=True`, you can embed HTML:

<div style="background-color: #e0f7fa; padding: 10px; border-radius: 5px;">
    <strong>This is an HTML block!</strong>
    <p>With nested elements and styling.</p>
</div>

<button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer;">
    Click me (won't do anything)
</button>
"""

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("Vizro Dash Components Demo"),
                html.Button("Toggle Dark/Light", id="theme-toggle", n_clicks=0),
            ],
            style={"display": "flex", "alignItems": "center", "gap": "20px"},
        ),
        html.Hr(),
        html.H2("Basic Markdown"),
        vizro_dash_components.Markdown(
            id="markdown-basic",
            children=markdown_content,
            link_target="_blank",
        ),
        html.Hr(),
        html.H2("Markdown with Math (mathjax=True)"),
        vizro_dash_components.Markdown(
            id="markdown-math",
            children=markdown_with_math,
            mathjax=True,
        ),
        html.Hr(),
        html.H2("Markdown with HTML (dangerously_allow_html=True)"),
        vizro_dash_components.Markdown(
            id="markdown-html",
            children=markdown_with_html,
            dangerously_allow_html=True,
        ),
    ],
    id="main-container",
    style={"padding": "20px", "maxWidth": "800px", "margin": "0 auto"},
)

# Clientside callback to toggle dark/light theme on <html> element.
# Sets data-mantine-color-scheme which Mantine CSS uses for theming,
# and also applies basic page-level dark/light styles.
clientside_callback(
    """
    function(n_clicks) {
        const html = document.documentElement;
        const current = html.getAttribute('data-mantine-color-scheme');
        const next = current === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-mantine-color-scheme', next);

        // Basic page styling for dark/light
        const container = document.getElementById('main-container');
        if (next === 'dark') {
            document.body.style.backgroundColor = '#1a1b1e';
            document.body.style.color = '#c1c2c5';
            container.style.color = '#c1c2c5';
        } else {
            document.body.style.backgroundColor = '#ffffff';
            document.body.style.color = '#000000';
            container.style.color = '#000000';
        }
        return next;
    }
    """,
    Output("theme-toggle", "children"),
    Input("theme-toggle", "n_clicks"),
    prevent_initial_call=True,
)

if __name__ == "__main__":
    app.run(debug=True)
