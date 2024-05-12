import plotly.express as px
from hamcrest import all_of, any_of, assert_that, contains_string, equal_to
from vizro_ai import VizroAI

vizro_ai = VizroAI()
df = px.data.gapminder()


def test_chart():
    vizro_ai._return_all_text = True
    resp = vizro_ai.plot(df, "describe the composition of scatter chart with gdp in continent")
    assert_that(
        resp["code_string"],
        all_of(contains_string("px.scatter")),
    )
    assert_that(
        resp["code_string"],
        any_of(contains_string("x='continent'"), contains_string("x='gdpPercap'")),
    )
    assert_that(
        resp["code_string"],
        any_of(contains_string("y='count'"), contains_string("y='gdpPercap'"), contains_string("y='continent'")),
    )
    assert_that(resp["business_insights"], equal_to(None))
    assert_that(resp["code_explanation"], equal_to(None))


def test_chart_with_explanation():
    vizro_ai._return_all_text = True
    resp = vizro_ai.plot(df, "describe the composition of gdp in US", explain=True)
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
