import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from typing import Literal, List, Dict
import os
from openai import OpenAI
import dash
from dash import (
    callback, Input, Output, State, ctx, html, dcc, 
    clientside_callback, ClientsideFunction, no_update
)
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
from vizro.models import VizroBaseModel
from vizro.models import Page
from dash_chat import ChatComponent as DashChatComponent
import json
from flask import request, Response

# Load environment variables
load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Initialize Vizro with assets folder
assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
vizro_app = Vizro(assets_folder=assets_path)

# TODO: It should be able to connect to any LLM
class ChatComponent(VizroBaseModel):
   """Chat component for Vizro dashboards."""
   
   type: Literal["chatcomponent"] = "chatcomponent"
   id: str 
   messages: List[Dict[str, str]] = [{"role": "assistant", "content": "Hello!"}]
   
   def build(self):
        return DashChatComponent(
           id=self.id,
           messages=self.messages,
           container_style={
               "backgroundColor": "var(--background-l0)",
               "color": "var(--text-primary)",
               "borderRadius": "8px",
               "padding": "16px",
               "border": "1px solid var(--border-primary)",
               "height": "calc(100vh - 200px)",  # Adjust this value as needed
               "minHeight": "400px",  # Set a minimum height
               "maxHeight": "calc(100vh - 200px)",  # Match height for consistency
               "display": "flex",
               "flexDirection": "column"
           },
           input_container_style={
               "borderTop": "1px solid var(--border-primary)",
               "padding": "16px 0 0 0",
               "marginTop": "16px",
               "marginTop": "auto"  # Push input to bottom
           },
           input_text_style={
               "backgroundColor": "var(--background-page)",
               "color": "var(--text-primary)",
               "border": "1px solid var(--border-primary)",
               "borderRadius": "4px",
               "padding": "8px 12px",
               "width": "100%"
           },
           fill_height=True,
           fill_width=True,
           typing_indicator="dots"
       )


# Register component
Page.add_type("components", ChatComponent)

class DashGPTComponent(VizroBaseModel):
    """DashGPT component for Vizro dashboards."""
    
    type: Literal["dashgpt"] = "dashgpt"
    id: str
    messages: List[Dict[str, str]] = [{"role": "assistant", "content": "Hello! I'm DashGPT, your data visualization assistant. How can I help you today?"}]
    
    def build(self):
        return html.Div([
            dcc.Store(id=f"{self.id}-messages", data=json.dumps(self.messages)),
            
            html.Div([
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
                    }
                ),
                
                html.Div([
                    dbc.InputGroup([
                        dbc.Textarea(
                            id=f"{self.id}-input",
                            placeholder="Ask me a question...",
                            style={
                                "height": "50px",
                                "resize": "none",
                                # "borderRadius": "8px 0 0 8px"
                            },
                            n_submit=0,  # Add this to enable Enter key submissions
                        ),
                        dbc.Button(
                            "Send", outline=True, color="secondary", className="me-1",
                            id=f"{self.id}-submit",
                            style={
                                # "borderRadius": "0 8px 8px 0",
                                # "backgroundColor": "var(--border-primary)",
                                # "backgroundColor": "#2d695e",
                                # "border": "none",
                                "height": "50px",
                            }
                        )
                    ])
                ], style={
                    "padding": "20px",
                    # "borderTop": "1px solid var(--border-primary)",
                    # "backgroundColor": "var(--background-l0)",
                    "flex": "0 0 auto",
                })
            ], style={
                "display": "flex",
                "flexDirection": "column",
                "height": "100%",
                "width": "100%",
                "background-color": "var(--mantine-color-dark-light)",
                # "border-left": "1px solid white",
            })
        ], style={
            "width": "90%", 
            "height": "90%", 
            "padding": "20px",
            "display": "flex",
        })

# Register component
Page.add_type("components", DashGPTComponent)

df = px.data.iris()

# First page - Main dashboard
page = vm.Page(
    title="Vizro on PyCafe",
    layout=vm.Layout(grid=[[0, 1], [2, 2], [2, 2], [3, 3], [3, 3]], row_min_height="140px"),
    components=[
        vm.Card(
            text="""
                ### What is Vizro?
                An open-source toolkit for creating modular data visualization applications.
                
                Rapidly self-serve the assembly of customized dashboards in minutes - without the need for advanced coding or design experience - to create flexible and scalable, Python-enabled data visualization applications."""
        ),
        vm.Card(
            text="""
                ### Github

                Checkout Vizro's GitHub page for further information and release notes. Contributions are always welcome!""",
            href="https://github.com/mckinsey/vizro",
        ),
        vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[vm.Filter(column="species"), vm.Filter(column="petal_length"), vm.Filter(column="sepal_width")],
)

# Second page - Chat dashboard
page_chat = vm.Page(
   title="Chat Dashboard",
   components=[
       ChatComponent(
           id="chat-component",
           messages=[{"role": "assistant", "content": "Hello!"}]
       )
   ],
#    layout=vm.Layout(grid=[[-1, 0, 0, -1], [-1, 0, 0, -1]]),
)

# Add callback to update UI
@callback(
    Output("chat-component", "messages"),
    Input("chat-component", "new_message"),
    State("chat-component", "messages"),
    prevent_initial_call=True,
)
def handle_chat(new_message, messages):
    if not new_message:
        raise PreventUpdate
    updated_messages = messages + [new_message]

    if new_message["role"] == "user":
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=updated_messages,
            temperature=1.0,
        )
        bot_response = {
            "role": "assistant",
            "content": response.choices[0].message.content.strip()
        }
        updated_messages.append(bot_response)
    return updated_messages

        


# Third page - DashGPT
page_dashgpt = vm.Page(
    title="DashGPT",
    components=[
        # vm.Card(
        #     text="""
        #         ### DashGPT Assistant
        #         An AI-powered assistant to help you analyze and understand your data visualization."""
        # ),
        DashGPTComponent(
            id="dashgpt-chat"
        )
    ],
    # layout=vm.Layout(grid=[
    #     [0, 0, 0, 0], 
    #     [1, 1, 1, 1], 
    #     [1, 1, 1, 1], 
    #     [1, 1, 1, 1], 
    #     [1, 1, 1, 1],
    #     ])
)

# Add callback to update UI
@callback(
    Output("dashgpt-chat-input", "value"),  # Only clear the input
    Input("dashgpt-chat-messages", "data"),
    prevent_initial_call=True
)
def update_chat_ui(messages_json):
    if not messages_json:
        raise PreventUpdate
    return ""  # Just clear the input

# Add clientside callback for user input and streaming
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="streaming_GPT"),
    Output("dashgpt-chat-messages", "data", allow_duplicate=True),
    [Input("dashgpt-chat-submit", "n_clicks"),
     Input("dashgpt-chat-input", "n_submit")],  # Add Enter key input
    [
        State("dashgpt-chat-input", "value"),
        State("dashgpt-chat-messages", "data"),
    ],
    prevent_initial_call=True
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
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return Response(response_stream(), mimetype="text/event-stream")

# Build and run the dashboard
dashboard = vm.Dashboard(pages=[page, page_chat, page_dashgpt])
vizro_app.build(dashboard).run()
