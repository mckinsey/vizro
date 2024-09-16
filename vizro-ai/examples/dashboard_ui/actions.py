"""Custom actions used within a dashboard."""

import base64
import os

from _utils import process_file
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
    ai_outputs = vizro_ai._dashboard(dfs, user_prompt, return_elements=True)

    return ai_outputs


@capture("action")
def data_upload_action(contents, filename):
    """Custom action to handle data upload for single or multiple files."""
    if not contents:
        raise PreventUpdate

    uploaded_data = {}
    if isinstance(filename, str):
        data = process_file(filename=filename, contents=contents)
        uploaded_data[filename] = data

    if isinstance(filename, list):
        for index, item in enumerate(filename):
            data = process_file(filename=item, contents=contents[index])
            uploaded_data[item] = data

    return uploaded_data


@capture("action")
def display_filename(data):
    """Custom action to display the uploaded filename."""
    if not data:
        raise PreventUpdate
    # Check for any error message in the data
    error_message = data.get("error_message")

    if error_message:
        return error_message

    filenames = ", ".join(data.keys())
    return f"Uploaded file name: '{filenames}'"


@capture("action")
def save_files(contents, filenames, last_modified):
    """Custom action to save the uploaded filenames."""
    if contents is not None:

        project_folder = "./output_files"
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)

        for content, filename in zip(contents, filenames):
            # Decode base64 encoded data
            content_type, content_string = content.split(",")
            decoded = base64.b64decode(content_string)

            # Save each file in the desired folder
            file_path = os.path.join(project_folder, filename)
            with open(file_path, "wb") as f:
                f.write(decoded)

        return last_modified
