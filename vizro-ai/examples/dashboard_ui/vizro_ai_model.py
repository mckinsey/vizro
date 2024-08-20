import base64
import io
import logging

import black
import pandas as pd
from dash import html
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
            df_dict = data
            df = pd.DataFrame(df_dict)
            api_key = api_data["api_key"]
            api_base = api_data["api_base"]
            ai_outputs = get_vizro_ai_plot(
                user_prompt=user_prompt, df=df, model=model, api_key=api_key, api_base=api_base
            )
            ai_code = ai_outputs.code
            figure = ai_outputs.figure
            code = black.format_str(ai_code, mode=black.Mode(line_length=100))

            ai_response = "\n".join(["```python", code, "```"])

        except Exception as exc:
            logging.exception(exc)
            ai_response = "Sorry, I can't do that. Check the console log for details."
            figure = go.Figure()

        return ai_response, figure


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

    return data


@capture("action")
def save_api_key(api_key, api_base, n_clicks):
    if n_clicks:
        return {"api_key": api_key, "api_base": api_base}
