"""Test usage of vizro_dash_components.Markdown with all features."""

import dash_mantine_components as dmc
import vizro_dash_components as vdc
from dash import Dash, html
from vizro_dash_components import Cascade

app = Dash(__name__)

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

And a code block with no language specified:

```
This is plain text in a code block.
No syntax highlighting applied.
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

app.layout = dmc.MantineProvider(
    dmc.Container(
        [
            dmc.Group(
                [
                    dmc.Title("Vizro Dash Components Demo", order=1),
                    dmc.ColorSchemeToggle(
                        lightIcon=html.Span("☀", style={"fontSize": 20}),
                        darkIcon=html.Span("☾", style={"fontSize": 20}),
                        size="lg",
                    ),
                ],
                justify="space-between",
                align="center",
                mb="md",
            ),
            dmc.Divider(mb="md"),
            dmc.Title("Basic Markdown", order=2, mb="sm"),
            vdc.Markdown(
                id="markdown-basic",
                children=markdown_content,
                link_target="_blank",
            ),
            dmc.Divider(my="md"),
            dmc.Title("Markdown with Math (mathjax=True)", order=2, mb="sm"),
            vdc.Markdown(
                id="markdown-math",
                children=markdown_with_math,
                mathjax=True,
            ),
            dmc.Divider(my="md"),
            dmc.Title("Markdown with HTML (dangerously_allow_html=True)", order=2, mb="sm"),
            vdc.Markdown(
                id="markdown-html",
                children=markdown_with_html,
                dangerously_allow_html=True,
            ),
            dmc.Divider(my="md"),
            dmc.Title("Cascade (single-select)", order=2, mb="sm"),
            Cascade(
                id="cascade-single",
                options=[
                    {
                        "label": "Asia",
                        "value": "asia",
                        "children": [
                            {"label": "Japan", "value": "japan"},
                            {"label": "China", "value": "china"},
                            {"label": "India", "value": "india"},
                        ],
                    },
                    {
                        "label": "Europe",
                        "value": "europe",
                        "children": [
                            {"label": "France", "value": "france"},
                            {"label": "Germany", "value": "germany"},
                        ],
                    },
                    {
                        "label": "Americas",
                        "value": "americas",
                        "children": [
                            {"label": "USA", "value": "usa"},
                            {"label": "Canada", "value": "canada"},
                            {"label": "Brazil", "value": "brazil"},
                        ],
                    },
                ],
            ),
            dmc.Divider(my="md"),
            dmc.Title("Cascade (multi-select)", order=2, mb="sm"),
            Cascade(
                id="cascade-multi",
                multi=True,
                options=[
                    {
                        "label": "Asia",
                        "value": "asia",
                        "children": [
                            {"label": "Japan", "value": "japan"},
                            {"label": "China", "value": "china"},
                            {"label": "India", "value": "india"},
                        ],
                    },
                    {
                        "label": "Europe",
                        "value": "europe",
                        "children": [
                            {"label": "France", "value": "france"},
                            {"label": "Germany", "value": "germany"},
                        ],
                    },
                ],
            ),
            dmc.Divider(my="md"),
            dmc.Title("Cascade (3-level hierarchy)", order=2, mb="sm"),
            Cascade(
                id="cascade-3level",
                options=[
                    {
                        "label": "Asia",
                        "value": "asia",
                        "children": [
                            {
                                "label": "East Asia",
                                "value": "east_asia",
                                "children": [
                                    {"label": "Japan", "value": "japan"},
                                    {"label": "South Korea", "value": "south_korea"},
                                ],
                            },
                            {
                                "label": "South Asia",
                                "value": "south_asia",
                                "children": [
                                    {"label": "India", "value": "india"},
                                    {"label": "Pakistan", "value": "pakistan"},
                                ],
                            },
                        ],
                    },
                ],
            ),
        ],
        size="md",
        py="xl",
    ),
    defaultColorScheme="light",
)

if __name__ == "__main__":
    app.run()
