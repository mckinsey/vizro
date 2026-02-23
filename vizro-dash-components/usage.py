"""Test usage of vizro_dash_components.Markdown with all features."""

import dash_mantine_components as dmc
import vizro_dash_components as vdc
from dash import Dash
from dash_iconify import DashIconify

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
                        lightIcon=DashIconify(icon="radix-icons:sun", width=20),
                        darkIcon=DashIconify(icon="radix-icons:moon", width=20),
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
        ],
        size="md",
        py="xl",
    ),
    defaultColorScheme="light",
)

if __name__ == "__main__":
    app.run()
