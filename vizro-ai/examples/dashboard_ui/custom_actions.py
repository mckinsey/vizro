import base64
import io
import logging

import black
import pandas as pd
from dash import html
from dash.exceptions import PreventUpdate
from langchain_openai import ChatOpenAI
from plotly import graph_objects as go
from vizro.models.types import capture
from vizro_ai import VizroAI


def get_vizro_ai_plot(user_prompt, df, model, api_key, api_base):
    llm = ChatOpenAI(model_name=model, openai_api_key=api_key, openai_api_base=api_base)
    vizro_ai = VizroAI(model=llm)
    ai_outputs = vizro_ai.plot(df, user_prompt, explain=False, return_elements=True)

    return ai_outputs


@capture("action")
def run_vizro_ai(user_prompt, n_clicks, data, model, api_data):
    """Gets the AI response and adds it to the chatbot window."""
    if n_clicks:
        try:
            if not data:
                ai_response = "Please upload data to proceed!"
                figure = go.Figure()
                plotly_fig = figure.to_json()

                return (
                    ai_response,
                    figure,
                    {"ai_response": ai_response, "figure": plotly_fig, "prompt": user_prompt, "filename": None},
                )

            df_dict = data["data"]
            filename = data["filename"]

            if api_data:
                api_key = api_data["api_key"]
                api_base = api_data["api_base"]
            else:
                ai_response = "Sorry, I can't do that. Please make sure you entered your API key!"
                figure = go.Figure()

                plotly_fig = figure.to_json()
                return (
                    ai_response,
                    figure,
                    {"ai_response": ai_response, "figure": plotly_fig, "prompt": user_prompt, "filename": filename},
                )

            df = pd.DataFrame(df_dict)

            ai_outputs = get_vizro_ai_plot(
                user_prompt=user_prompt, df=df, model=model, api_key=api_key, api_base=api_base
            )
            ai_code = ai_outputs.code
            figure = ai_outputs.figure
            plotly_fig = figure.to_json()
            code = black.format_str(ai_code, mode=black.Mode(line_length=100))

            ai_response = "\n".join(["```python", code, "```"])

        except Exception as exc:
            logging.exception(exc)
            ai_response = f"Sorry, I can't do that. Error: {exc}"
            figure = go.Figure()
            plotly_fig = figure.to_json()

        return (
            ai_response,
            figure,
            {"ai_response": ai_response, "figure": plotly_fig, "prompt": user_prompt, "filename": filename},
        )


@capture("action")
def data_upload_action(contents, filename):
    """Custom data upload action."""
    if contents:
        content_type, content_string = contents.split(",")

        decoded = base64.b64decode(content_string)

    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    data = df.to_dict("records")
    data_dict = {"data": data, "filename": filename}

    return data_dict


@capture("action")
def save_api_key(api_key, api_base, n_clicks):
    if n_clicks:
        return {"api_key": api_key, "api_base": api_base}


@capture("action")
def toggle_api_key_visibility(visible):
    if visible:
        return "text"
    else:
        return "password"


@capture("action")
def upload_data_action(data):
    if not data:
        raise PreventUpdate

    filename = data["filename"]
    # TODO: Add validation for file type
    return f"Uploaded file name: '{filename}'"
