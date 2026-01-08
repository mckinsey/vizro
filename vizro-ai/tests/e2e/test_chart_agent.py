import os

import plotly.express as px
from dotenv import load_dotenv
from hamcrest import any_of, assert_that, contains_string, is_not, matches_regexp
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from vizro_ai.agents import chart_agent
from vizro_ai.agents.response_models import ChartPlan

load_dotenv()

df = px.data.gapminder()

POSSIBLE_AXIS_VALUES = ["count", "gdpPercap", "continent", "avg_gdpPercap", "mean_gdpPercap", "total_gdpPercap"]
POSSIBLE_CHART = ["px.bar", "go.Bar"]

model = OpenAIChatModel(
    "gpt-4o-mini",
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
    x_conditions = create_axis_conditions("x", POSSIBLE_AXIS_VALUES)
    y_conditions = create_axis_conditions("y", POSSIBLE_AXIS_VALUES)
    charts = [contains_string(chart) for chart in POSSIBLE_CHART]

    resp = chart_agent.run_sync(
        model=model,
        user_prompt="Create a bar chart comparing GDP across different continents",
        deps=df,
    ).output
    assert_that(resp.chart_code, any_of(*charts))
    assert_that(resp.chart_code, any_of(*x_conditions))
    assert_that(resp.chart_code, any_of(*y_conditions))


def test_chart_with_explanation():
    y_conditions = create_axis_conditions("y", POSSIBLE_AXIS_VALUES)
    charts = [contains_string(chart) for chart in POSSIBLE_CHART]

    resp = chart_agent.run_sync(
        model=model,
        output_type=ChartPlan,
        user_prompt="describe the composition of gdp per year in US using bar chart",
        deps=df,
    ).output
    assert_that(
        resp.code,
        any_of(*charts),
    )
    assert_that(
        resp.code,
        any_of(
            matches_regexp(r".*x='year'.*"),
            matches_regexp(r'.*x="year".*'),
            matches_regexp(r".*x=\w*\['year'\].*"),
            matches_regexp(r'.*x=\w*\["year"\].*'),
        ),
    )
    assert_that(resp.code, any_of(*y_conditions))
    assert_that(
        resp.chart_insights,
        any_of(
            contains_string("GDP per capita"),
            contains_string("GDP"),
        ),
    )
    assert_that(
        resp.chart_insights,
        any_of(
            contains_string("United States"),
            contains_string("US"),
        ),
    )
    assert_that(resp.chart_insights, is_not(None))
