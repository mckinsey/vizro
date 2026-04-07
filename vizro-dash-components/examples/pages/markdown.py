"""Full-suite demo for the Markdown component."""

# ruff: noqa: D103

import dash
import dash_mantine_components as dmc
import vizro_dash_components as vdc
from dash import html

dash.register_page(__name__)

HEADINGS = """
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
"""

PARAGRAPHS = """
This is a regular paragraph with **bold**, *italic*, ~~strikethrough~~, and `inline code`.

Here is a [link to example.com](https://example.com) and a second paragraph to show spacing.

> This is a blockquote.
> It can span multiple lines.
"""

LISTS = """
Unordered list:

- Item A
- Item B
  - Nested B1
  - Nested B2
- Item C

Ordered list:

1. First
2. Second
   1. Sub-second
   2. Sub-second again
3. Third
"""

CODE_PYTHON = """
```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

print(greet("World"))
```
"""

CODE_JS = """
```javascript
function greet(name) {
  return `Hello, ${name}!`;
}

console.log(greet("World"));
```
"""

CODE_SQL = """
```sql
SELECT
    country,
    COUNT(*) AS order_count,
    SUM(amount) AS total_revenue
FROM orders
WHERE created_at >= '2024-01-01'
GROUP BY country
ORDER BY total_revenue DESC;
```
"""

TABLE = """
| Component | Type       | Async chunk |
|-----------|------------|-------------|
| Markdown  | React/TSX  | Yes         |
| Cascader  | React/TSX  | No          |
| MathJax   | Extension  | Yes         |
"""

MATHJAX_INLINE = r"Einstein's famous equation: $E = mc^2$"

MATHJAX_BLOCK = r"""
The quadratic formula:

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

Maxwell's equations in differential form:

$$\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}$$
"""

LINKS = """
Links with `link_target="_blank"` open in a new tab:

- [Vizro on GitHub](https://github.com/mckinsey/vizro)
- [Dash documentation](https://dash.plotly.com)
- [Mantine components](https://mantine.dev)
"""


def section(title, description, component):
    return html.Div(
        [
            dmc.Title(title, order=2, mb=4),
            dmc.Text(description, c="dimmed", size="sm", mb="sm") if description else None,
            component,
            dmc.Divider(mt="xl", mb="xl"),
        ]
    )


layout = html.Div(
    [
        section("Headings", "All six heading levels.", vdc.Markdown(HEADINGS)),
        section(
            "Text formatting",
            "Bold, italic, strikethrough, inline code, blockquote.",
            vdc.Markdown(PARAGRAPHS),
        ),
        section("Lists", "Unordered and ordered, with nesting.", vdc.Markdown(LISTS)),
        section("Table", "GFM pipe-table syntax.", vdc.Markdown(TABLE)),
        section(
            "Code block — Python",
            "Syntax highlighting via dmc.CodeHighlight (requires MantineProvider).",
            vdc.Markdown(CODE_PYTHON),
        ),
        section("Code block — JavaScript", None, vdc.Markdown(CODE_JS)),
        section("Code block — SQL", None, vdc.Markdown(CODE_SQL)),
        section(
            "MathJax — inline",
            "mathjax=True enables LaTeX rendering. Inline: $...$",
            vdc.Markdown(MATHJAX_INLINE, mathjax=True),
        ),
        section(
            "MathJax — block",
            "Display equations: $$...$$",
            vdc.Markdown(MATHJAX_BLOCK, mathjax=True),
        ),
        section(
            "Links with link_target",
            'link_target="_blank" opens links in a new tab.',
            vdc.Markdown(LINKS, link_target="_blank"),
        ),
        html.Div(style={"height": "200px"}),
    ]
)
