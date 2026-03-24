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

POSSIBLE_CHART = ["px.bar", "go.Bar", "add_bar"]

model = OpenAIChatModel(
    "gpt-5-nano-2025-08-07",
    provider=OpenAIProvider(base_url=os.getenv("OPENAI_API_BASE"), api_key=os.getenv("OPENAI_API_KEY")),
)


def create_axis_conditions(axis: str, values: list[str]) -> list:
    return [
        matches_regexp(f".*{pattern}.*")
        for value in values
        for pattern in [
            f"{axis}='{value}'",
            f'{axis}="{value}"',
            f"{axis}=\\w*\\['{value}'\\]",
            f'{axis}=\\w*\\["{value}"\\]',
        ]
    ]


def test_chart():
    possible_x_axis_values = [
        "continent",
    ]
    possible_y_axis_values = [
        "gdpPercap",
    ]
    x_conditions = create_axis_conditions("x", possible_x_axis_values)
    y_conditions = create_axis_conditions("y", possible_y_axis_values)
    charts = [contains_string(chart) for chart in POSSIBLE_CHART]

    resp = chart_agent.run_sync(
        model=model,
        user_prompt="""
        Create a bar chart comparing GDP across different continents.
        X axis should represent continents and have x=coninent in figure settings.
        Y axis should represent the GDP values and have y=gdpPercap in figure settings.""",
        deps=df,
    ).output
    assert_that(resp.chart_code, any_of(*charts))
    assert_that(resp.chart_code, any_of(*x_conditions))
    assert_that(resp.chart_code, any_of(*y_conditions))


def test_chart_with_explanation():
    possible_x_axis_values = [
        "year",
    ]
    possible_y_axis_values = [
        "gdpPercap",
    ]
    charts = [contains_string(chart) for chart in POSSIBLE_CHART]
    x_conditions = create_axis_conditions("x", possible_x_axis_values)
    y_conditions = create_axis_conditions("y", possible_y_axis_values)

    resp = chart_agent.run_sync(
        model=model,
        output_type=ChartPlan,
        user_prompt="""
        describe the composition of gdp per year in US using bar chart.
        X axis should represent year and have x=year in figure settings.
        Y axis should represent the GDP values and have y=gdpPercap in figure settings.""",
        deps=df,
    ).output
    assert_that(resp.code, any_of(*charts))
    assert_that(resp.code, any_of(*x_conditions))
    assert_that(resp.code, any_of(*y_conditions))
    assert_that(
        resp.chart_insights,
        any_of(
            contains_string("United States"),
            contains_string("US"),
        ),
    )
