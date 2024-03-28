import time

import plotly.express as px
import pytest
from hamcrest import all_of, any_of, assert_that, contains_string, equal_to
from vizro_ai import VizroAI

vizro_ai = VizroAI()
df = px.data.gapminder()


@pytest.mark.parametrize(
    "model_name",
    ["gpt-3.5-turbo-0613", "gpt-4-0613"],
    ids=["gpt-3.5", "gpt-4.0"],
)
def test_chart(model_name):
    vizro_ai._return_all_text = True
    vizro_ai.model_name = model_name
    before = time.time()
    resp = vizro_ai.plot(df, "describe the composition of scatter chart with gdp in continent")
    after = time.time()
    print("RESPONSE TIME:", after - before)  # noqa: T201
    assert_that(
        resp["code_string"],
        all_of(contains_string("px.scatter"), contains_string("x='continent'"), contains_string("y='gdpPercap'")),
    )
    assert_that(resp["business_insights"], equal_to(None))
    assert_that(resp["code_explanation"], equal_to(None))


@pytest.mark.parametrize(
    "model_name",
    ["gpt-3.5-turbo-0613", "gpt-4-0613"],
    ids=["gpt-3.5", "gpt-4.0"],
)
def test_chart_with_explanation(model_name):
    vizro_ai._return_all_text = True
    vizro_ai.model_name = model_name
    before = time.time()
    resp = vizro_ai.plot(df, "describe the composition of gdp in US", explain=True)
    after = time.time()
    print("RESPONSE TIME (explanation):", after - before)  # noqa: T201
    assert_that(
        resp["code_string"],
        all_of(contains_string("px.bar"), contains_string("x='year'"), contains_string("y='gdpPercap'")),
    )
    assert_that(
        resp["business_insights"], any_of(contains_string("GDP in the United States"), contains_string("GDP in the US"))
    )
    assert_that(
        resp["code_explanation"],
        all_of(contains_string("https://vizro.readthedocs.io/en/stable/pages/user_guides/custom_charts/")),
    )
