"""AI plot example."""

import time

from dash_extensions import SSE
from dash import Dash, html, dcc, callback, Output, Input
from dash_extensions.streaming import sse_message, sse_options
from flask import Response, request

# Create a small example app.
app = Dash(__name__)
app.layout = html.Div(
    [
        html.Button("Start streaming", id="btn"),
        SSE(id="sse", concat=True, animate_chunk=5, animate_delay=50),
        html.Div(id="response"),
    ]
)
# Render (concatenated, animated) text from the SSE component.
app.clientside_callback(
    "function(x){return x};",
    Output("response", "children"),
    Input("sse", "animation"),
)


@app.callback(
    Output("sse", "url"),
    Output("sse", "options"),
    Input("btn", "n_clicks"),
    prevent_initial_call=True,
)
def start_streaming(_):
    return "/stream", sse_options("Hello, world!\nHello, world!\nHello, world! \n Hello, world!")


@app.server.post("/stream")
def stream():
    message = request.data.decode("utf-8")

    def eventStream():
        for char in message:
            time.sleep(0.1)
            print(sse_message(char))
            yield sse_message(char)
        yield sse_message()
    

    return Response(eventStream(), mimetype="text/event-stream")


server = app.server  # make server available for gunicorn

if __name__ == "__main__":
    app.run()