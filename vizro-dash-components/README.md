# Vizro Dash Components

Vizro Dash Components are used by the Vizro framework but can be used in a pure Dash app. Use as `import vizro_dash_components as vdc`.

See the [example Dash app](examples) and its [live demo on PyCafe](https://py.cafe/vizro-official/vizro-dash-components) for a full demo of all components.

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

Hierarchical cascading dropdown inspired by [Ant Design Cascader](https://ant.design/components/cascader) and [`fac.AntdCascader`](https://fac.feffery.tech/AntdCascader). Users navigate a tree of options via side-by-side panels and select leaf values. Supports single-select and multi-select. It accepts all the same arguments as [`dcc.Dropdown`](https://dash.plotly.com/dash-core-components/dropdown) (for example `className`, `style`, `clearable`, `searchable`, `search_value`, `placeholder`, `disabled`, `multi`, `optionHeight`, `maxHeight`, `debounce`, `closeOnSelect`, `labels`, and persistence props) and is built to visually match it. Use `help(vdc.Cascader)` for the full list.

#### `options` format

`options` for [`dcc.Dropdown`](https://dash.plotly.com/dash-core-components/dropdown) describes a flat list and can be given in two different formats: a shorthand and an explicit option dict. `options` for `vdc.Cascader` describes a tree and can similarly be given in two different formats:

1. **Shorthand**

    - `dcc.Dropdown`: a list, for example `["New York City", "Montreal"]`.
    - `vdc.Cascader`: a nested dict/list, for example `{"USA": ["New York City", "Boston"], "Canada": ["Toronto", "Montreal"]}`.

1. **Explicit option dicts**

    - `dcc.Dropdown`: a list of dicts, each with `label` and `value`, plus optional keys such as `disabled` and `search`.
    - `vdc.Cascader`: a list of dicts, each with `label` and `value`, plus optional keys such as `disabled` and `search`. Parents also have `children`, a list of child dicts; leaves omit `children`.

Only leaf values appear in the `vdc.Cascader` component’s `value` (single value or list when `multi=True`).

```python
from dash import Dash, Input, Output, html
import vizro_dash_components as vdc

OPTIONS = {
    "Asia": {
        "Japan": ["Tokyo", "Osaka", "Kyoto"],
        "China": ["Beijing", "Shanghai", "Guangzhou"],
    },
    "Europe": {
        "France": ["Paris", "Lyon", "Marseille"],
        "Germany": ["Berlin", "Munich", "Hamburg"],
    },
}

# Same tree in explicit form.
# label doesn't need to match value any more.
# Optional on any dict: disabled, search.
# OPTIONS = [
#     {
#         "label": "Asia",
#         "value": "Asia",
#         "children": [
#             {
#                 "label": "Japan",
#                 "value": "Japan",
#                 "children": [
#                     {"label": "Tokyo", "value": "Tokyo"},
#                     {"label": "Osaka", "value": "Osaka"},
#                     {"label": "Kyoto", "value": "Kyoto"},
#                 ],
#             },
#             {
#                 "label": "China",
#                 "value": "China",
#                 "children": [
#                     {"label": "Beijing", "value": "Beijing"},
#                     {"label": "Shanghai", "value": "Shanghai"},
#                     {"label": "Guangzhou", "value": "Guangzhou"},
#                 ],
#             },
#         ],
#     },
#     ... similarly for Europe
# ]

app = Dash(__name__)
app.layout = [
    vdc.Cascader(id="regions", options=OPTIONS, placeholder="Select a city..."),
    html.Div(id="out"),
]


@app.callback(Output("out", "children"), Input("regions", "value"))
def show(value):
    return f"Selected leaf value: {value!r}"


if __name__ == "__main__":
    app.run()
```

## Development

Contributor workflows (Hatch, npm, regenerating `vizro_dash_components/`) are documented in [AGENTS.md](AGENTS.md) (same content as [CLAUDE.md](CLAUDE.md) for Claude Code).
