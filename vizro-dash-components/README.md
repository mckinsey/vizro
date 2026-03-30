# Vizro Dash Components

Vizro Dash Components are used by the Vizro framework but can be used in a pure Dash app.

See the [example Dash app](examples) and its [live demo on PyCafe](https://py.cafe/vizro-official/vizro-dash-components) for a full showcase of all components.

## Installation

```bash
pip install vizro-dash-components
```

## Components

### Markdown

Based on [`dcc.Markdown`](https://dash.plotly.com/dash-core-components/markdown), with identical properties. Renders Markdown content with syntax-highlighted code blocks via [`dmc.CodeHighlight`](https://www.dash-mantine-components.com/components/code-highlight) and [`dmc.InlineCodeHighlight`](https://www.dash-mantine-components.com/components/inline-code-highlight). Requires a [`dmc.MantineProvider`](https://www.dash-mantine-components.com/components/mantine-provider) wrapper.

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
            ```
            """,
    )
)

if __name__ == "__main__":
    app.run()
````

### Cascader

Hierarchical cascading dropdown inspired by [Ant Design Cascader](https://ant.design/components/cascader) and [`fac.AntdCascader`](https://fac.feffery.tech/AntdCascader). Users navigate a tree of options via side-by-side panels and select leaf values. Supports single-select and multi-select. It accepts most of the same keyword arguments as [`dcc.Dropdown`](https://dash.plotly.com/dash-core-components/dropdown) and is built to visually match it.

**`options`** must be a **tree** (not a single flat list of siblings like a typical `dcc.Dropdown`). The **explicit** form is still the same idea as [`dcc.Dropdown` `options`](https://dash.plotly.com/dash-core-components/dropdown): each entry is a dict with `label` and `value`, but hierarchy is expressed with nested **`children`** lists instead of many items at one level.

- **Explicit list of nodes** — A list of dicts. Each dict has `label` and `value`. Parents add **`children`**: a list of child dicts. Leaves omit `children`. You can also set optional fields on any node, same spirit as richer dropdown options: **`disabled`**, **`title`** (native tooltip), and **`search`** (string used for search instead of `label`).
- **Nested dict / list shorthand** — As in the example below. Each dict key is a parent node (the key is used as both `label` and `value`). The value is either another nested dict (deeper levels) or a list of leaves. List entries are usually scalars (each scalar is both `label` and `value`), or you can use **full dicts** (`label`, `value`, and the optional keys above) where you need different labels, disabled rows, etc.

**`value`** always reflects **leaf** choices only: a single string or number, or `null` when `multi=False`; a list of leaf values when `multi=True`.

When **`searchable=True`** (default), search matches **leaves and parent branches** (by `label` or `search`). Choosing a **branch** row clears the query and opens the side-by-side columns at that node; it does not change `value`.

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
}

app = Dash(__name__)

app.layout = [
    vdc.Cascader(id="cascade", options=OPTIONS, placeholder="Select a city..."),
    html.Div(id="cascade-output"),
]


@app.callback(Output("cascade-output", "children"), Input("cascade", "value"))
def show_selected(value):
    return f"Selected: {value}"


if __name__ == "__main__":
    app.run()
```

## Development

Contributor workflows (Hatch, npm, regenerating `vizro_dash_components/`) are documented in [AGENTS.md](AGENTS.md) (same content as [CLAUDE.md](CLAUDE.md) for Claude Code).
