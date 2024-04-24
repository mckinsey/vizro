import csv
import time
from datetime import datetime

import plotly.express as px
import pytest
from hamcrest import all_of, any_of, assert_that, contains_string, equal_to
from vizro_ai import VizroAI

vizro_ai = VizroAI()
df = px.data.gapminder()
today = datetime.today()
formatted_date = today.strftime("%Y-%m-%d")


@pytest.mark.parametrize(
    "model_name",
    ["gpt-3.5-turbo", "gpt-4-0613"],
    ids=["gpt-3.5", "gpt-4.0"],
)
def test_chart(model_name):
    vizro_ai._return_all_text = True
    vizro_ai.model_name = model_name
    before = time.time()
    resp = vizro_ai.plot(df, "describe the composition of scatter chart with gdp in continent")
    after = time.time()
    resp_time = after - before
    print("RESPONSE TIME:", after - before)  # noqa: T201
    assert_that(
        resp["code_string"],
        all_of(contains_string("px.scatter"), contains_string("x='continent'"), contains_string("y='gdpPercap'")),
    )
    assert_that(resp["business_insights"], equal_to(None))
    assert_that(resp["code_explanation"], equal_to(None))
    with open(f"report_test_chart_{formatted_date}.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([f"{model_name}", f"{resp_time}"])


@pytest.mark.parametrize(
    "model_name",
    ["gpt-3.5-turbo", "gpt-4-0613"],
    ids=["gpt-3.5", "gpt-4.0"],
)
def test_chart_with_explanation(model_name):
    vizro_ai._return_all_text = True
    vizro_ai.model_name = model_name
    before = time.time()
    resp = vizro_ai.plot(df, "describe the composition of gdp in US", explain=True)
    after = time.time()
    resp_time = after - before
    print("RESPONSE TIME (explanation):", after - before)  # noqa: T201
    assert_that(
        resp["code_string"],
        all_of(contains_string("px.bar"), contains_string("x='year'")),
    )
    assert_that(
        resp["code_string"],
        any_of(contains_string("y='gdpPercap'"), contains_string("y='total_gdp'")),
    )
    assert_that(
        resp["business_insights"],
        any_of(
            contains_string("GDP per capita in the United States"),
            contains_string("GDP in the United States"),
            contains_string("GDP in the US"),
        ),
    )
    assert_that(
        resp["code_explanation"],
        all_of(contains_string("https://vizro.readthedocs.io/en/stable/pages/user_guides/custom_charts/")),
    )
    with open(f"report_test_chart_with_explanation_{formatted_date}.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([f"{model_name}", f"{resp_time}"])
