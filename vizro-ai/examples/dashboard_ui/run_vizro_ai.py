"""File running Vizro AI."""

import argparse
import json
import logging

import black
import pandas as pd
from actions import get_vizro_ai_dashboard
from dash.exceptions import PreventUpdate


def run_vizro_ai_dashboard(user_prompt, model, api_key, api_base, n_clicks, data, vendor):  # noqa: PLR0913
    """Function for running VizroAI."""
    data = json.loads(data)

    if not n_clicks:
        raise PreventUpdate

    if not data:
        return "Please upload data to proceed!"

    if not api_key:
        return "API key not found. Make sure you enter your API key!"

    try:
        df = pd.DataFrame(data["data"])
        ai_outputs = get_vizro_ai_dashboard(
            user_prompt=user_prompt, dfs=df, model=model, api_key=api_key, api_base=api_base, vendor_input=vendor
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
    parser.add_argument("--arg1", required=True, help="User prompt")
    parser.add_argument("--arg2", required=True, help="Model")
    parser.add_argument("--arg3", required=True, help="API key")
    parser.add_argument("--arg4", required=True, help="API base")
    parser.add_argument("--arg5", required=True, help="n_clicks")
    parser.add_argument("--arg6", required=True, help="Data")
    parser.add_argument("--arg7", required=True, help="Vendor")

    args = parser.parse_args()

    print(
        run_vizro_ai_dashboard(args.arg1, args.arg2, args.arg3, args.arg4, args.arg5, args.arg6, args.arg7)
    )  # noqa: T201
