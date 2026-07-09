import json

import pandas as pd
import pytest
from pydantic_ai import ModelResponse, TextPart, models
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

from vizro_ai.agents import chart_agent

models.ALLOW_MODEL_REQUESTS = False


def _valid_chart_plan_model(messages, info):
    # The model returns a declarative plan (data), not code.
    content = json.dumps({"chart_type": "bar", "encodings": {"x": "x", "y": "y"}})
    return ModelResponse(parts=[TextPart(content=content)])


def test_add_df_with_valid_dataframe():
    df = pd.DataFrame({"x": range(10), "y": range(10, 20)})
    function_model = FunctionModel(_valid_chart_plan_model)
    with chart_agent.override(model=function_model):
        result = chart_agent.run_sync(model=function_model, user_prompt="test", deps=df)
    messages = result.all_messages()
    assert any("A sample of the data is" in str(msg) for msg in messages)
    assert result.output.chart_type == "bar"


def test_add_df_with_fewer_than_five_rows():
    """Pre-aggregated dataframes are often tiny; sampling the prompt rows must not crash."""
    df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    function_model = FunctionModel(_valid_chart_plan_model)
    with chart_agent.override(model=function_model):
        result = chart_agent.run_sync(model=function_model, user_prompt="test", deps=df)
    assert result.output.chart_type == "bar"


def test_output_validator_retries_on_plan_data_mismatch():
    """A plan that does not fit the data goes back to the model as a retry, not to the user."""
    df = pd.DataFrame({"x": range(10), "y": range(10, 20)})
    calls = []

    def flaky_model(messages, info):
        calls.append(1)
        encodings = {"x": "nope"} if len(calls) == 1 else {"x": "x", "y": "y"}
        return ModelResponse(parts=[TextPart(content=json.dumps({"chart_type": "bar", "encodings": encodings}))])

    function_model = FunctionModel(flaky_model)
    with chart_agent.override(model=function_model):
        result = chart_agent.run_sync(model=function_model, user_prompt="test", deps=df)
    assert len(calls) == 2
    assert result.output.encodings == {"x": "x", "y": "y"}


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
