"""Custom actions used within a dashboard."""

import base64
import io
import logging

import pandas as pd
from _utils import check_file_extension
from dash.exceptions import PreventUpdate
from langchain_openai import ChatOpenAI
from vizro.models.types import capture
from vizro_ai import VizroAI

SUPPORTED_VENDORS = {"OpenAI": ChatOpenAI}


def get_vizro_ai_dashboard(user_prompt, dfs, model, api_key, api_base, vendor_input):  # noqa: PLR0913
    """VizroAi dashboard configuration."""
    vendor = SUPPORTED_VENDORS[vendor_input]
    llm = vendor(model_name=model, openai_api_key=api_key, openai_api_base=api_base)
    vizro_ai = VizroAI(model=llm)
    ai_outputs = vizro_ai._dashboard([dfs], user_prompt, return_elements=True)

    return ai_outputs


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
