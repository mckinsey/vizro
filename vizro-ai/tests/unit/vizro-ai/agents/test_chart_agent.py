import json

import pandas as pd
import pytest
from pydantic_ai import ModelResponse, TextPart, models
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

from vizro_ai.agents import chart_agent

models.ALLOW_MODEL_REQUESTS = False


def _valid_chart_plan_model(messages, info):
    chart_code = 'def custom_chart(data_frame):\n    return px.bar(data_frame, x="x", y="y")'
    content = json.dumps(
        {
            "chart_type": "bar",
            "imports": ["import plotly.express as px"],
            "chart_code": chart_code,
        }
    )
    return ModelResponse(parts=[TextPart(content=content)])


def test_add_df_with_valid_dataframe():
    df = pd.DataFrame({"x": range(10), "y": range(10, 20)})
    function_model = FunctionModel(_valid_chart_plan_model)
    with chart_agent.override(model=function_model):
        result = chart_agent.run_sync(model=function_model, user_prompt="test", deps=df)
    messages = result.all_messages()
    assert any("A sample of the data is" in str(msg) for msg in messages)


def test_add_df_with_none_raises():
    test_model = TestModel()
    with chart_agent.override(model=test_model):
        with pytest.raises(ValueError, match="DataFrame dependency is required"):
            chart_agent.run_sync(model=test_model, user_prompt="test", deps=None)


def test_add_df_with_invalid_type_raises():
    test_model = TestModel()
    with chart_agent.override(model=test_model):
        with pytest.raises(ValueError, match="must be a pandas DataFrame"):
            chart_agent.run_sync(model=test_model, user_prompt="test", deps="not a dataframe")
