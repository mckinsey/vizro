import vizro.plotly.express as px
from hamcrest import any_of, assert_that, contains_string, is_not, matches_regexp

from vizro_ai import VizroAI

vizro_ai = VizroAI()
df = px.data.gapminder()

POSSIBLE_AXIS_VALUES = ["count", "gdpPercap", "continent", "avg_gdpPercap", "mean_gdpPercap", "total_gdpPercap"]
POSSIBLE_CHART = ["px.bar", "go.Bar"]


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

    resp = vizro_ai.plot(
        df=df,
        user_input="Create a bar chart comparing GDP across different continents",
        return_elements=True,
    )
    assert_that(
        resp.code,
        any_of(*charts),
    )
    assert_that(resp.code, any_of(*x_conditions))
    assert_that(resp.code, any_of(*y_conditions))


def test_chart_with_explanation():
    y_conditions = create_axis_conditions("y", POSSIBLE_AXIS_VALUES)
    charts = [contains_string(chart) for chart in POSSIBLE_CHART]

    vizro_ai._return_all_text = True
    resp = vizro_ai.plot(df, "describe the composition of gdp per year in US using bar chart", return_elements=True)
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
    assert_that(resp.code_explanation, is_not(None))
