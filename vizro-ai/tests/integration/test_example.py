import re
import vizro.plotly.express as px
from hamcrest import assert_that, contains_string, matches_regexp, any_of
from vizro_ai import VizroAI

vizro_ai = VizroAI()
df = px.data.gapminder()

# List of possible values for axis variables
POSSIBLE_VALUES = ["count", "gdpPercap", "continent", "avg_gdpPercap", "mean_gdpPercap", "total_gdpPercap"]

def check_axis(axis, code):
    """Check if the specified axis in the code uses one of the possible values."""
    pattern = rf'{axis}\s*=\s*([^,\n]+)'
    match = re.search(pattern, code)
    if match:
        value = match.group(1).strip().strip('\'"')
        return value in POSSIBLE_VALUES
    return False

def test_scatter_plot():
    """Test creation of a scatter plot comparing GDP across different continents."""
    resp = vizro_ai.plot(
        df=df,
        user_input="Create a scatter plot comparing GDP across different continents",
        return_elements=True,
    )

    # Check if the response contains a scatter plot
    assert_that(resp.code, any_of(contains_string("px.scatter"), contains_string("go.Scatter")))

    # Check if x and y axes use valid values
    assert_that(check_axis('x', resp.code), f"X-axis not in {POSSIBLE_VALUES}")
    assert_that(check_axis('y', resp.code), f"Y-axis not in {POSSIBLE_VALUES}")

def test_bar_chart_with_explanation():
    """Test creation of a bar chart describing GDP composition per year in the US."""
    vizro_ai._return_all_text = True
    resp = vizro_ai.plot(df, "describe the composition of gdp per year in US using bar chart", return_elements=True)

    # Check if the response contains a bar chart
    assert_that(resp.code, any_of(contains_string("px.bar"), contains_string("go.Bar")))

    # Check if x-axis is set to 'year'
    assert_that(resp.code, any_of(
        contains_string("x='year'"),
        matches_regexp(r"x\s*=\s*\w+\s*\[\s*['\"]year['\"]\s*\]")
    ))

    # Check if y-axis uses one of the possible values
    y_conditions = [
        any_of(
            contains_string(f"y='{value}'"),
            matches_regexp(rf"y\s*=\s*\w+\s*\[\s*['\"]({value}|{value.lower()})['\"]")
        )
        for value in POSSIBLE_VALUES
    ]
    assert_that(resp.code, any_of(*y_conditions))

    # Check if chart insights mention GDP and United States
    assert_that(resp.chart_insights, any_of(
        contains_string("GDP per capita"),
        contains_string("GDP")
    ))
    assert_that(resp.chart_insights, any_of(
        contains_string("United States"),
        contains_string("US")
    ))
