
from _utils import construct_message

import argparse
import json
import logging

import black
import pandas as pd
from actions import get_vizro_ai_dashboard
from dash.exceptions import PreventUpdate


from vizro_ai._llm_models import _get_llm_model




def run_image_ai(images, model, api_key, api_base, n_clicks, data, vendor):
    """Running vizro ai image."""
    ai_model = _get_llm_model(model="gpt-4o")
    question = """
    You are a front-end developer with expertise in Plotly, Dash, and the visualization library named Vizro.
    1. Describe how many dashboard pages do you see.
    2. Describe what do you see in each page with following aspects:

    <Vizro Components>
    you might see `Card (which is a container holding text)`, `Graph`, or `AgGrid`.
    For `Graph`, Describe the chart type and describe what you see for x-axis, y-axis, and legend. 

    <Vizro Filter>
    you might see filters using different selectors, including `Dropdown`, `Checklist`, `RadioItems`, `RangeSlider`, `Slider`, `DatePicker`.

    <Vizro Layout>
    Only describe the positions of all Vizro Components (`Card`, `Graph`, `AgGrid`). 
    When describing layout, AVOID the positions of `Filter`.

    Important, if there are any text you see, accurately describe the original text. 
    """
    if not n_clicks:
        raise PreventUpdate

    if not data:
        return "Please upload data to proceed!"
    if not api_key:
        return "API key not found. Make sure you enter your API key!"
    images = json.loads(images)
    images = list(images.values())

    message = construct_message(images, question)
    response = ai_model.invoke([message])
    dashboard_spec = response.content

    try:
        dfs = [pd.DataFrame(item) for item in json.loads(data).values()]
        ai_outputs = get_vizro_ai_dashboard(
            user_prompt=dashboard_spec, dfs=dfs, model=model, api_key=api_key, api_base=api_base, vendor_input=vendor
        )
        ai_code = ai_outputs.code
        formatted_code = black.format_str(ai_code, mode=black.Mode(line_length=90))

        ai_response = "\n".join(["```python", formatted_code, "```"])
        return ai_response

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

