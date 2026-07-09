import os

import plotly.express as px
from dotenv import load_dotenv
from hamcrest import any_of, assert_that, contains_string, matches_regexp
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from vizro_ai.agents import chart_agent
from vizro_ai.agents.response_models import ChartPlan

load_dotenv()

df = px.data.gapminder()

POSSIBLE_CHART = ["px.bar", "px.histogram"]

model = OpenAIChatModel(
    "gpt-5-nano-2025-08-07",
    provider=OpenAIProvider(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY")),
)


def create_axis_conditions(axis: str, values: list[str]) -> list:
    return [matches_regexp(f".*{axis}='{value}'.*") for value in values]


def test_chart():
    # `resp` is a declarative BaseChartPlan; `resp.code` is the plotly-express code templated from it.
    resp = chart_agent.run_sync(
        model=model,
        user_prompt="""
        Create a bar chart comparing GDP across different continents.
        X axis should represent continents (x=continent). Y axis the GDP values (y=gdpPercap).""",
        deps=df,
    ).output
    assert_that(resp.code, any_of(*[contains_string(c) for c in POSSIBLE_CHART]))
    assert_that(resp.code, any_of(*create_axis_conditions("x", ["continent"])))
    assert_that(resp.code, any_of(*create_axis_conditions("y", ["gdpPercap"])))


def test_chart_with_explanation():
    resp = chart_agent.run_sync(
        model=model,
        output_type=ChartPlan,
        user_prompt="""
        Describe the composition of gdp per year in the US using a bar chart.
        X axis should represent year (x=year). Y axis the GDP values (y=gdpPercap).""",
        deps=df,
    ).output
    assert_that(resp.code, any_of(*[contains_string(c) for c in POSSIBLE_CHART]))
    assert_that(resp.code, any_of(*create_axis_conditions("x", ["year"])))
    assert_that(resp.chart_insights, any_of(contains_string("United States"), contains_string("US")))
