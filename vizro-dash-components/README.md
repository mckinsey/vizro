# Vizro Dash Components

Vizro Dash Components are used by the Vizro framework but can be used in a pure Dash app.

## Installation

```bash
pip install vizro-dash-components
```

## Components

### Markdown

Renders Markdown content with syntax-highlighted code blocks (via `dmc.CodeHighlight`) and optional MathJax support.

Requires a `dmc.MantineProvider` wrapper for code block styling.

````python
import dash_mantine_components as dmc
import vizro_dash_components as vdc
from dash import Dash

app = Dash(__name__)

app.layout = dmc.MantineProvider(
    vdc.Markdown(
        id="my-markdown",
        children="""
# Hello World

```python
print("Hello, World!")
````

```
    """,
)
```

)

if __name__ == "__main__": app.run(debug=True)

````

### Cascade

A hierarchical cascading dropdown. Users navigate a tree of options via side-by-side panels and select leaf values. Supports single-select and multi-select. Visually matches `dcc.Dropdown`.

Requires a `dmc.MantineProvider` wrapper.

```python
import dash_mantine_components as dmc
import vizro_dash_components as vdc
from dash import Dash, Input, Output

OPTIONS = [
    {
        "label": "Asia",
        "value": "asia",
        "children": [
            {"label": "Japan", "value": "japan"},
            {"label": "China", "value": "china"},
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
]

app = Dash(__name__)

app.layout = dmc.MantineProvider(
    vdc.Cascade(id="cascade", options=OPTIONS, placeholder="Select a country...")
)

@app.callback(Output("cascade", "value"), Input("cascade", "value"))
def on_change(value):
    print(f"Selected: {value}")
    return value

if __name__ == "__main__":
    app.run(debug=True)
````
