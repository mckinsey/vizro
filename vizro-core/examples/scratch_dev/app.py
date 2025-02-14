from vizro import Vizro
import vizro.models as vm
from typing import Literal, List, Dict
import os
from openai import OpenAI
from dash import callback, Input, Output, State, html, dcc, clientside_callback, ClientsideFunction, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
from vizro.models import VizroBaseModel
from vizro.models import Page
import json
from flask import request, Response

# Load environment variables
load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Initialize Vizro with assets folder
assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
vizro_app = Vizro(assets_folder=assets_path)


class CNXAssistantComponent(VizroBaseModel):
    """CNX Assistant component for Vizro dashboards."""

    type: Literal["cnx_assistant"] = "cnx_assistant"
    id: str
    messages: List[Dict[str, str]] = [
        {"role": "assistant", "content": "Hello! I'm your CNX Assistant. How can I help you today?"}
    ]

    def build(self):
        return html.Div(
            [
                dcc.Store(id=f"{self.id}-messages", data=json.dumps(self.messages)),
                html.Div(
                    [
                        html.Div(
                            id=f"{self.id}-history",
                            style={
                                "overflowY": "auto",
                                "padding": "20px",
                                "gap": "10px",
                                "width": "100%",
                                "flex": "1 1 auto",
                                "display": "flex",
                                "flexDirection": "column",
                            },
                        ),
                        html.Div(
                            [
                                dbc.InputGroup(
                                    [
                                        dbc.Textarea(
                                            id=f"{self.id}-input",
                                            placeholder="Ask me a question...",
                                            style={
                                                "height": "80px",
                                                "resize": "none",
                                            },
                                            n_submit=0,  # Add this to enable Enter key submissions
                                        ),
                                        dbc.Button(
                                            "Send",
                                            outline=True,
                                            color="secondary",
                                            className="me-1",
                                            id=f"{self.id}-submit",
                                            style={
                                                "height": "80px",
                                            },
                                        ),
                                    ]
                                )
                            ],
                            style={
                                "padding": "20px",
                                "flex": "0 0 auto",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "height": "100%",
                        "width": "100%",
                        "background-color": "var(--mantine-color-dark-light)",
                    },
                ),
            ],
            style={
                "width": "90%",
                "height": "90%",
                "padding": "20px",
                "display": "flex",
            },
        )


# Register component
Page.add_type("components", CNXAssistantComponent)


# Third page - CNX Assistant
page_cnx = vm.Page(
    title="CNX Assistant",
    components=[CNXAssistantComponent(id="cnx-assistant")],
)


# Add callback to update UI
@callback(
    Output("cnx-assistant-input", "value"),  # Only clear the input
    Input("cnx-assistant-messages", "data"),
    prevent_initial_call=True,
)
def update_chat_ui(messages_json):
    if not messages_json:
        raise PreventUpdate
    return ""  # Just clear the input


# Add clientside callback for user input and streaming
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="streaming_GPT"),
    Output("cnx-assistant-messages", "data", allow_duplicate=True),
    [Input("cnx-assistant-submit", "n_clicks"), Input("cnx-assistant-input", "n_submit")],  # Add Enter key input
    [
        State("cnx-assistant-input", "value"),
        State("cnx-assistant-messages", "data"),
    ],
    prevent_initial_call=True,
)


# Register the streaming route
@vizro_app.dash.server.route("/streaming-chat", methods=["POST"])
def streaming_chat():
    data = request.json
    user_prompt = data["prompt"]
    messages = json.loads(data.get("chat_history", "[]"))

    def response_stream():
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages + [{"role": "user", "content": user_prompt}],
            temperature=1.0,
            stream=True,
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return Response(response_stream(), mimetype="text/event-stream")


# Build and run the dashboard
dashboard = vm.Dashboard(pages=[page_cnx])
vizro_app.build(dashboard).run()
