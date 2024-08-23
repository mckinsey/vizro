import vizro.plotly.express as px
from hamcrest import all_of, any_of, assert_that, contains_string, equal_to
from vizro_ai import VizroAI

vizro_ai = VizroAI()
df = px.data.gapminder()


def test_chart():
    possible_values = ["count", "gdpPercap", "continent", "avg_gdpPercap", "mean_gdpPercap", "total_gdpPercap"]
    xy_conditions = [contains_string(f"{axis}='{value}'") for axis in ["x", "y"] for value in possible_values]

    resp = vizro_ai.plot(
        df=df,
        user_input="describe the composition of scatter chart with gdp in continent",
        explain=False,
        return_elements=True,
    )
    assert_that(
        resp.code,
        all_of(contains_string("px.scatter")),
    )
    assert_that(resp.code, any_of(*xy_conditions))
    assert_that(resp.code_explanation, equal_to(None))
    assert_that(resp.business_insights, equal_to(None))


def test_chart_with_explanation():
    possible_values = ["count", "gdpPercap", "continent", "avg_gdpPercap", "mean_gdpPercap", "total_gdpPercap"]
    y_conditions = [contains_string(f"y='{value}'") for value in possible_values]

    vizro_ai._return_all_text = True
    resp = vizro_ai.plot(
        df, "describe the composition of gdp per year in US using bar chart", explain=True, return_elements=True
    )
    assert_that(
        resp.code,
        all_of(contains_string("px.bar"), contains_string("x='year'")),
    )
    assert_that(resp.code, any_of(*y_conditions)),
    assert_that(
        resp.business_insights,
        any_of(
            contains_string("GDP per capita"),
            contains_string("GDP"),
        ),
    )
    assert_that(
        resp.business_insights,
        any_of(
            contains_string("United States"),
            contains_string("US"),
        ),
    )
    assert_that(
        resp.code_explanation,
        all_of(contains_string("https://vizro.readthedocs.io/en/stable/pages/user_guides/custom_charts/")),
    )
