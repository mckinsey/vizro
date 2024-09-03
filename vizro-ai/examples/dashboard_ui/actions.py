"""Custom actions used within a dashboard."""

import base64
import io
import logging

import black
import pandas as pd
from _utils import check_file_extension
from dash.exceptions import PreventUpdate
from langchain_openai import ChatOpenAI
from plotly import graph_objects as go
from vizro.models.types import capture
from vizro_ai import VizroAI

SUPPORTED_VENDORS = {"OpenAI": ChatOpenAI}


def get_vizro_ai_plot(user_prompt, df, model, api_key, api_base, vendor_input):  # noqa: PLR0913
    """VizroAi plot configuration."""
    vendor = SUPPORTED_VENDORS[vendor_input]
    llm = vendor(model_name=model, openai_api_key=api_key, openai_api_base=api_base)
    vizro_ai = VizroAI(model=llm)
    ai_outputs = vizro_ai.plot(df, user_prompt, explain=False, return_elements=True)

    return ai_outputs


@capture("action")
def run_vizro_ai(user_prompt, n_clicks, data, model, api_key, api_base, vendor_input):  # noqa: PLR0913
    """Gets the AI response and adds it to the text window."""

    def create_response(ai_response, figure, user_prompt, filename):
        plotly_fig = figure.to_json()
        return (
            ai_response,
            figure,
            {"ai_response": ai_response, "figure": plotly_fig, "prompt": user_prompt, "filename": filename},
        )

    if not n_clicks:
        raise PreventUpdate

    if not data:
        ai_response = "Please upload data to proceed!"
        figure = go.Figure()
        return create_response(ai_response, figure, user_prompt, None)

    if not api_key:
        ai_response = "API key not found. Make sure you enter your API key!"
        figure = go.Figure()
        return create_response(ai_response, figure, user_prompt, data["filename"])

    if api_key.startswith('"'):
        ai_response = "Make sure you enter your API key without quotes!"
        figure = go.Figure()
        return create_response(ai_response, figure, user_prompt, data["filename"])

    if api_base is not None and api_base.startswith('"'):
        ai_response = "Make sure you enter your API base without quotes!"
        figure = go.Figure()
        return create_response(ai_response, figure, user_prompt, data["filename"])

    try:
        df = pd.DataFrame(data["data"])
        ai_outputs = get_vizro_ai_plot(
            user_prompt=user_prompt,
            df=df,
            model=model,
            api_key=api_key,
            api_base=api_base,
            vendor_input=vendor_input,
        )
        ai_code = ai_outputs.code
        figure = ai_outputs.figure
        formatted_code = black.format_str(ai_code, mode=black.Mode(line_length=100))

        ai_response = "\n".join(["```python", formatted_code, "```"])
        return create_response(ai_response, figure, user_prompt, data["filename"])

    except Exception as exc:
        logging.exception(exc)
        ai_response = f"Sorry, I can't do that. Following Error occurred: {exc}"
        figure = go.Figure()
        return create_response(ai_response, figure, user_prompt, data["filename"])


@capture("action")
def data_upload_action(contents, filename):
    """Custom data upload action."""
    if not contents:
        raise PreventUpdate

    if not check_file_extension(filename=filename):
        return {"error_message": "Unsupported file extension.. Make sure to upload either csv or an excel file."}

    content_type, content_string = contents.split(",")

    try:
        decoded = base64.b64decode(content_string)
        if filename.endswith(".csv"):
            # Handle CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        else:
            # Handle Excel file
            df = pd.read_excel(io.BytesIO(decoded))

        data = df.to_dict("records")
        return {"data": data, "filename": filename}

    except Exception as e:
        logging.exception(e)
        return {"error_message": "There was an error processing this file."}


@capture("action")
def display_filename(data):
    """Custom action to display uploaded filename."""
    if data is None:
        raise PreventUpdate

    display_message = data.get("filename") or data.get("error_message")
    return f"Uploaded file name: '{display_message}'" if "filename" in data else display_message
