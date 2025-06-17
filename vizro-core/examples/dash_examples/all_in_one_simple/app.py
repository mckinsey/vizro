from aio_components import MarkdownWithColorAIO
from dash import Dash, Input, Output, callback, html

app = Dash()

app.layout = html.Div(
    [
        MarkdownWithColorAIO("Custom callback", aio_id="color-picker"),
        html.Div(id="color-picker-output"),
        MarkdownWithColorAIO("Test", aio_id="color-picker-2"),
        html.Div(id="color-picker-output-2"),
    ],
)


@callback(Output("color-picker-output", "children"), Input(MarkdownWithColorAIO.ids.dropdown("color-picker"), "value"))
def display_color(value):
    return f"You have selected {value}"


if __name__ == "__main__":
    app.run(debug=True)
