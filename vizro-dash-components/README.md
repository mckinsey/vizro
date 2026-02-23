# Vizro Dash Components

Vizro Dash Components are used by the Vizro framework but can be used in a pure Dash app.

## Installation

```bash
pip install vizro-dash-components
```

## Usage

````python
from dash import Dash
from vizro_dash_components import Markdown

app = Dash(__name__)

app.layout = Markdown(
    id="my-markdown",
    children="""
    # Hello World

    ```python
    print("Hello, World!")
    ```
    """,
)

if __name__ == "__main__":
    app.run(debug=True)
````
