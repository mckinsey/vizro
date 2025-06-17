import time

import dash
from dash import Input, Output, callback, clientside_callback, dcc, html

dash.register_page(__name__)


class Callbacks:
    @staticmethod
    def define_callbacks(identifier: str = "default"):
        @callback(Output("callbacks-output", "children"), Input("callbacks-input", "value"))
        def update_title(input_value):
            return f"You selected: {input_value} with identifier {identifier}"

        clientside_callback(
            f"""
            function(value) {{
                return "Boolean selection: " + value + " with identifier {identifier}";
            }}
            """,
            Output("callbacks-output-2", "children"),
            Input("callbacks-input-2", "value"),
        )


# Callbacks.define_callbacks()


def layout(**kwargs):
    print("kwargs", kwargs)
    # Callbacks.define_callbacks("layout")

    print(dash._callback.GLOBAL_CALLBACK_LIST)
    # print("==>", dash._callback.GLOBAL_CALLBACK_MAP)
    # print(dash._callback.GLOBAL_INLINE_SCRIPTS)
    # print(dash._pages.PAGE_REGISTRY)
    # print(dash._pages.CONFIG)
    # print(dash._pages.CONFIG.__dict__)
    print("=" * 50)
    return html.Div(
        [
            html.H1(
                f"Page that defines callbacks inside or outside of the layout function, {time.strftime('%H:%M:%S')}"
            ),
            html.H1("Server-side callback", id="callbacks-output"),
            html.H2("Server-side callback, select a color: "),
            dcc.RadioItems(options=["Red", "Green", "Blue"], value="Red", id="callbacks-input"),
            html.Br(),
            html.H1("Clientside callback", id="callbacks-output-2"),
            html.H2("Clientside callback, select a boolean: "),
            html.H2("Select a boolean: "),
            dcc.RadioItems(options=["yes", "no"], value="yes", id="callbacks-input-2"),
        ]
    )


# layout = layout_fn()
