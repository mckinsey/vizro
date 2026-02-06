"""Dev app to try things out - testing vizro_dash_components.Markdown with Vizro theme toggle.

Tests direct vdc.Markdown usage (via vm.Figure) and Vizro models that
internally use vdc.Markdown: vm.Text and vm.Card.
"""

import pandas as pd
import vizro.models as vm
import vizro_dash_components as vdc
from dash import html
from vizro import Vizro
from vizro.models.types import capture

# Sample data for demonstration
df = pd.DataFrame(
    {
        "topic": ["Python", "JavaScript", "SQL", "React"],
        "description": [
            "A versatile programming language",
            "The language of the web",
            "Database query language",
            "A JavaScript library for building UIs",
        ],
        "code_example": [
            '```python\ndef hello():\n    return "Hello, World!"\n```',
            '```javascript\nconst hello = () => "Hello, World!";\n```',
            "```sql\nSELECT * FROM users WHERE active = true;\n```",
            "```jsx\nconst App = () => <h1>Hello, World!</h1>;\n```",
        ],
        "formula": [
            r"$f(x) = x^2 + 2x + 1$",
            r"$y = mx + b$",
            r"$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$",
            r"$E = mc^2$",
        ],
    }
)


@capture("figure")
def markdown_figure(
    data_frame: pd.DataFrame,
    topic_column: str = "topic",
    description_column: str = "description",
    code_column: str = "code_example",
    show_code: bool = True,
) -> html.Div:
    """Creates a Markdown component displaying information from a DataFrame."""
    if data_frame.empty:
        content = "# No data available\n\nPlease adjust your filters."
    else:
        row = data_frame.iloc[0]
        topic = row[topic_column]
        description = row[description_column]
        code = row[code_column] if show_code else ""

        content = f"""
# {topic}

{description}

{code if show_code else ""}

---
*This content updates based on the selected filter.*
"""

    return html.Div(
        [
            vdc.Markdown(
                id="dynamic-markdown",
                children=content,
                dedent=True,
            )
        ]
    )


@capture("figure")
def markdown_with_math(
    data_frame: pd.DataFrame,
    topic_column: str = "topic",
    formula_column: str = "formula",
) -> html.Div:
    """Creates a Markdown component with math formulas from a DataFrame."""
    if data_frame.empty:
        content = "# No data available"
    else:
        row = data_frame.iloc[0]
        topic = row[topic_column]
        formula = row[formula_column]

        content = f"""
## Math Example: {topic}

Here's a mathematical formula related to {topic}:

{formula}

The formula above is rendered using KaTeX.
"""

    return html.Div(
        [
            vdc.Markdown(
                id="math-markdown",
                children=content,
                mathjax=True,
                dedent=True,
            )
        ]
    )


@capture("figure")
def markdown_documentation(
    data_frame: pd.DataFrame,
    n_items: int = 2,
) -> html.Div:
    """Creates a documentation-style Markdown showing multiple items."""
    items = data_frame.head(n_items)

    sections = []
    for _, row in items.iterrows():
        sections.append(f"""
### {row["topic"]}

{row["description"]}

{row["code_example"]}
""")

    content = f"""
# Programming Languages Reference

Showing {len(items)} of {len(data_frame)} topics.

{"".join(sections)}

---
*Adjust the slider to show more or fewer topics.*
"""

    return html.Div(
        [
            vdc.Markdown(
                id="docs-markdown",
                children=content,
                dedent=True,
            )
        ]
    )


# Create the Vizro dashboard
page_basic = vm.Page(
    title="Basic Markdown Figure",
    components=[
        vm.Figure(
            id="markdown-fig",
            figure=markdown_figure(
                data_frame=df,
                topic_column="topic",
                description_column="description",
                code_column="code_example",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="topic",
            selector=vm.RadioItems(title="Select a topic"),
        ),
    ],
)

page_math = vm.Page(
    title="Markdown with Math",
    components=[
        vm.Figure(
            id="math-fig",
            figure=markdown_with_math(
                data_frame=df,
                topic_column="topic",
                formula_column="formula",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="topic",
            selector=vm.Dropdown(title="Select a topic"),
        ),
    ],
)

page_docs = vm.Page(
    title="Dynamic Documentation",
    components=[
        vm.Figure(
            id="docs-fig",
            figure=markdown_documentation(data_frame=df),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["docs-fig.n_items"],
            selector=vm.Slider(
                min=1,
                max=4,
                step=1,
                value=2,
                title="Number of topics to display",
            ),
        ),
    ],
)

# --- Pages using Vizro models that internally use vdc.Markdown ---

# vm.Text and vm.Card - both render markdown via vdc.Markdown
page_text_card = vm.Page(
    title="Text and Card",
    components=[
        vm.Text(
            text="""## vm.Text Component

This text is rendered by `vm.Text`, which internally uses `vdc.Markdown`.

- Supports **bold**, *italic*, and `inline code`
- Supports [links](https://vizro.readthedocs.io/)

```python
page = vm.Page(components=[vm.Text(text="Hello!")])
```
"""
        ),
        vm.Card(
            text="""### Card with Code

Cards also use `vdc.Markdown` for their text content.

```bash
pip install vizro
```
""",
            header="Card Header (markdown)",
            footer="Card Footer — *powered by vdc.Markdown*",
        ),
    ],
)

dashboard = vm.Dashboard(
    title="Vizro Markdown Component Demo",
    pages=[page_basic, page_math, page_docs, page_text_card],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
