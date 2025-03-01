"""Custom actions used within a dashboard."""

import base64
import io
import logging

import black
import dash
import dash_bootstrap_components as dbc
import pandas as pd
from _utils import check_file_extension
from dash.exceptions import PreventUpdate
from langchain_openai import ChatOpenAI
from plotly import graph_objects as go
from vizro.models.types import capture
from vizro_ai import VizroAI

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_mistralai import ChatMistralAI
except ImportError:
    ChatMistralAI = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # TODO: remove manual setting and make centrally controlled

SUPPORTED_VENDORS = {
    "OpenAI": ChatOpenAI,
    "Anthropic": ChatAnthropic,
    "Mistral": ChatMistralAI,
    "xAI": ChatOpenAI,
}

SUPPORTED_MODELS = {
    "OpenAI": [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
    ],
    "Anthropic": [
        "claude-3-opus-latest",
        "claude-3-5-sonnet-latest",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    "Mistral": ["mistral-large-latest", "open-mistral-nemo", "codestral-latest"],
    "xAI": ["grok-beta"],
}
DEFAULT_TEMPERATURE = 0.1
DEFAULT_RETRY = 3


def get_vizro_ai_plot(user_prompt, df, model, api_key, api_base, vendor_input):
    """VizroAi plot configuration."""
    vendor = SUPPORTED_VENDORS[vendor_input]

    if vendor_input == "OpenAI":
        llm = vendor(
            model_name=model, openai_api_key=api_key, openai_api_base=api_base, temperature=DEFAULT_TEMPERATURE
        )
    if vendor_input == "Anthropic":
        llm = vendor(
            model=model, anthropic_api_key=api_key, anthropic_api_url=api_base, temperature=DEFAULT_TEMPERATURE
        )
    if vendor_input == "Mistral":
        llm = vendor(model=model, mistral_api_key=api_key, mistral_api_url=api_base, temperature=DEFAULT_TEMPERATURE)
    if vendor_input == "xAI":
        llm = vendor(model=model, openai_api_key=api_key, openai_api_base=api_base, temperature=DEFAULT_TEMPERATURE)

    vizro_ai = VizroAI(model=llm)
    ai_outputs = vizro_ai.plot(
        df,
        user_prompt,
        max_debug_retry=DEFAULT_RETRY,
        return_elements=True,
        _minimal_output=True,
        validate_code=True,
    )

    return ai_outputs


@capture("action")
def run_vizro_ai(user_prompt, n_clicks, data, model, api_key, api_base, vendor_input):  # noqa: PLR0913
    """Gets the AI response and adds it to the text window."""

    def create_response(ai_response, figure, ai_outputs):
        return (ai_response, figure, {"ai_outputs": ai_outputs})

    if not n_clicks:
        raise PreventUpdate

    if not data:
        ai_response = "Please upload data to proceed!"
        figure = go.Figure()
        return create_response(ai_response, figure, ai_outputs=None)

    if not api_key:
        ai_response = "API key not found. Make sure you enter your API key!"
        figure = go.Figure()
        return create_response(ai_response, figure, ai_outputs=None)

    if api_key.startswith('"'):
        ai_response = "Make sure you enter your API key without quotes!"
        figure = go.Figure()
        return create_response(ai_response, figure, ai_outputs=None)

    if api_base is not None and api_base.startswith('"'):
        ai_response = "Make sure you enter your API base without quotes!"
        figure = go.Figure()
        return create_response(ai_response, figure, ai_outputs=None)

    try:
        logger.info("Attempting chart code.")
        df = pd.DataFrame(data["data"])
        ai_outputs = get_vizro_ai_plot(
            user_prompt=user_prompt,
            df=df,
            model=model,
            api_key=api_key,
            api_base=api_base,
            vendor_input=vendor_input,
        )
        ai_code = ai_outputs.code_vizro
        figure_vizro = ai_outputs.get_fig_object(data_frame=df, vizro=True)
        figure_plotly = ai_outputs.get_fig_object(data_frame=df, vizro=False)
        formatted_code = black.format_str(ai_code, mode=black.Mode(line_length=100))
        ai_code_outputs = {
            "vizro": {"code": ai_outputs.code_vizro, "fig": figure_vizro.to_json()},
            "plotly": {"code": ai_outputs.code, "fig": figure_plotly.to_json()},
        }

        ai_response = "\n".join(["```python", formatted_code, "```"])
        logger.info("Successful query produced.")
        return create_response(ai_response, figure_vizro, ai_outputs=ai_code_outputs)

    except Exception as exc:
        logger.debug(exc)
        logger.info("Chart creation failed.")
        ai_response = f"Sorry, I can't do that. Following Error occurred: {exc}"
        figure = go.Figure()
        return create_response(ai_response, figure, ai_outputs=None)


@capture("action")
def data_upload_action(contents, filename):
    """Custom data upload action."""
    if not contents:
        raise PreventUpdate

    if not check_file_extension(filename=filename):
        return (
            {"error_message": "Unsupported file extension.. Make sure to upload either csv or an excel file."},
            {"color": "gray"},
            {"display": "none"},
        )

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
        return {"data": data, "filename": filename}, {"cursor": "pointer"}, {}

    except Exception as e:
        logger.debug(e)
        return (
            {"error_message": "There was an error processing this file."},
            {"color": "gray", "cursor": "default"},
            {"display": "none"},
        )


@capture("action")
def display_filename(data):
    """Custom action to display uploaded filename."""
    if data is None:
        raise PreventUpdate

    display_message = data.get("filename") or data.get("error_message")
    return f"Uploaded file name: '{display_message}'" if "filename" in data else display_message


@capture("action")
def update_table(data):
    """Custom action for updating data."""
    if not data:
        return dash.no_update
    df = pd.DataFrame(data["data"])
    filename = data.get("filename") or data.get("error_message")
    modal_title = f"Data sample preview for {filename} file"
    df_sample = df.sample(5)
    table = dbc.Table.from_dataframe(df_sample, striped=False, bordered=True, hover=True)
    return table, modal_title
