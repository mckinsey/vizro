# Vizro Dash Components

Vizro Dash Components are used by the Vizro framework but can be used in a pure Dash app.

See the [example Dash app](examples) and its [live demo on PyCafe](https://py.cafe/vizro-official/vizro-dash-components) for a full showcase of all components.

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

if __name__ == "__main__": app.run()

````

### Cascader

A hierarchical cascading dropdown inspired by Ant Design's Cascader pattern. Users navigate a tree of options via side-by-side panels and select leaf values. Supports single-select and multi-select. Built to visually match [`dcc.Dropdown`](https://dash.plotly.com/dash-core-components/dropdown).

```python
import vizro_dash_components as vdc
from dash import Dash, Input, Output, html

OPTIONS = {
    "Asia": {
        "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama"],
        "China": ["Beijing", "Shanghai", "Shenzhen", "Guangzhou"],
        "India": ["Mumbai", "Delhi", "Bangalore", "Chennai"],
    },
    "Europe": {
        "France": ["Paris", "Lyon", "Marseille", "Toulouse"],
        "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt"],
        "UK": ["London", "Manchester", "Birmingham", "Edinburgh"],
    },
    "Americas": {
        "USA": ["New York", "Los Angeles", "Chicago", "Houston"],
        "Brazil": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador"],
        "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary"],
    },
}

app = Dash(__name__)

app.layout = [
    vdc.Cascader(
        id="cascade", options=OPTIONS, placeholder="Select a city..."
    ),
    html.Div(id="cascade-output"),
]


@app.callback(Output("cascade-output", "children"), Input("cascade", "value"))
def show_selected(value):
    return f"Selected: {value}"


if __name__ == "__main__":
    app.run()
```
````
