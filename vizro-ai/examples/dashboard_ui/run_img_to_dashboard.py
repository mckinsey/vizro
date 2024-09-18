
from _utils import construct_message

import argparse
import json
import logging

import black
import pandas as pd
from actions import get_vizro_ai_dashboard
from dash.exceptions import PreventUpdate
from langchain_openai import ChatOpenAI
import base64
from PIL import Image
import numpy as np


from vizro_ai._llm_models import _get_llm_model

output_start = "###OUTPUT_START###"
output_end = "###OUTPUT_END###"
req_start = "###REQUIREMENT_START###"
req_end = "###REQUIREMENT_END###"

# # Find the start of the existing code block
# start_index = result.stdout.find("```")
# existing_output = result.stdout[start_index:]



def load_image(image_path):
    """
    Load an image from a local file path, convert it to base64,
    and return as a numpy array and base64 string.
    """
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")
    
    img = Image.open(image_path)
    return np.array(img), image_data

def get_image_data(**kwargs):
    """
    Load images and return a list of their base64-encoded data.
    
    :param kwargs: Should contain 'image_paths' key with a list of file paths
    :return: List of base64-encoded image data
    """
    image_paths = kwargs.get('image_paths', [])
    return [load_image(path)[1] for path in image_paths]


def run_image_ai(images, model, api_key, api_base, n_clicks, data, vendor):
    """Running vizro ai image."""
    # ai_model = _get_llm_model(model="gpt-4o")
    ai_model = ChatOpenAI(
        model_name=model, 
        temperature=0, 
        openai_api_key=api_key,
        openai_api_base=api_base,
        )
    question = """
You are a front-end developer specializing in Plotly, Dash, and the Vizro visualization library. Your task is to accurately convert a user sketch of the dashboard design into the Vizro design pattern.

<Dashboard Overview>:
Identify the number of dashboard pages visible.

<Page Details>:
For each page, describe the following aspects:

<Vizro Components>:

List components such as Card (text container), Graph, or AgGrid.
For Graph, specify the chart type and describe the x-axis, y-axis, and legend content.

<Vizro Filters>:

Note any filters such as Dropdown, Checklist, RadioItems, RangeSlider, Slider, and DatePicker.
IMPORTANT: Do NOT include filters in the layout description. Simply list them here.

<Vizro Layout> (Layout of Vizro Components):

Describe only the positions of Card, Graph, and AgGrid. Do NOT describe the positions of filters in the layout.
Use layout terms like Row, Column, and Grid.
Be precise: specify the position of each component (e.g., Row 1, Column 2). take into account roughly how much space each component occupies.

Text Accuracy:
Accurately transcribe any visible text as it appears.

Sticky Notes:
If text appears on a yellow sticky note, it is a description of a Vizro component (e.g., a graph, not a card). Imagine and describe the component based on the sticky note text.
"""
    if not n_clicks:
        raise PreventUpdate

    if not data:
        return "Please upload data to proceed!"
    if not api_key:
        return "API key not found. Make sure you enter your API key!"
    # images = json.loads(images)
    # images = list(images.values())
    image_paths = [
    "/Users/lingyi_zhang/vizx/os/vizro/vizro-ai/examples/dashboard_ui/page1.png",
    "/Users/lingyi_zhang/vizx/os/vizro/vizro-ai/examples/dashboard_ui/page2.png",
    ]
    images = get_image_data(image_paths=image_paths)

    df1 = pd.read_csv("/Users/lingyi_zhang/vizx/os/vizro/vizro-ai/examples/dashboard_ui/coaches.csv")
    df2 = pd.read_csv("/Users/lingyi_zhang/vizx/os/vizro/vizro-ai/examples/dashboard_ui/medals.csv")

    message = construct_message(images, question)
    response = ai_model.invoke([message])
    dashboard_spec = response.content
    # return "```"+dashboard_spec

    try:
        # dfs = [pd.DataFrame(item) for item in json.loads(data).values()]
        ai_outputs = get_vizro_ai_dashboard(
            user_prompt=dashboard_spec, dfs=[df1, df2], model=model, api_key=api_key, api_base=api_base, vendor_input=vendor
        )
        ai_code = ai_outputs.code
        formatted_code = black.format_str(ai_code, mode=black.Mode(line_length=90))

        ai_response = "\n".join(["```python", formatted_code, "```"])

        # Combine everything with delimiters
        stdout_result = f"""
{output_start}
{ai_response}
{output_end}

{req_start}
{dashboard_spec}
{req_end}
"""
        return stdout_result

    except Exception as exc:
        logging.exception(exc)
        ai_response = f"Sorry, I can't do that. Following Error occurred: {exc}"
        return ai_response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some arguments.")
    parser.add_argument("--arg1", required=True, help="Images")
    parser.add_argument("--arg2", required=True, help="Model")
    parser.add_argument("--arg3", required=True, help="API key")
    parser.add_argument("--arg4", required=True, help="API base")
    parser.add_argument("--arg5", required=True, help="n_clicks")
    parser.add_argument("--arg6", required=True, help="Data")
    parser.add_argument("--arg7", required=True, help="Vendor")

    args = parser.parse_args()

    print(run_image_ai(args.arg1, args.arg2, args.arg3, args.arg4, args.arg5, args.arg6, args.arg7))

