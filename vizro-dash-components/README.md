# Vizro Dash Components

Vizro Dash Components are used by the Vizro framework but can be used in a pure Dash app.

## Installation

```bash
pip install vizro-dash-components
```

## Usage

The `Markdown` component requires a `dmc.MantineProvider` wrapper for proper styling of code blocks.

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
    app.run(debug=True)
````
