############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro.models.types import capture
from vizro import Vizro
import pandas as pd
from vizro.managers import data_manager
import vizro.plotly.express as px
from vizro.models.types import capture


# Load gapminder data and filter for 8 Southeast Asian countries
gapminder_full = px.data.gapminder()

# Select 8 Southeast Asian countries with varying development levels
selected_countries = [
    "Singapore",      # High development
    "Malaysia",       # Upper middle income
    "Thailand",       # Upper middle income
    "Indonesia",      # Lower middle income
    "Philippines",    # Lower middle income
    "Vietnam",        # Lower middle income
    "Cambodia",       # Lower income
    "Myanmar"         # Lower income
]

# Filter the data for these countries
gapminder = gapminder_full[gapminder_full["country"].isin(selected_countries)]


@capture("graph")
def bump_chart_with_highlighting(data_frame, highlight_country=None):
    # Calculate rankings for each year
    data_with_rank = data_frame.copy()
    data_with_rank['rank'] = data_frame.groupby('year')['lifeExp'].rank(method='dense', ascending=False)
    
    # Create bump chart (line chart with rankings)
    fig = px.line(
        data_with_rank,
        x="year",
        y="rank",
        color="country",
        markers=True,
        hover_data={"lifeExp": ":.1f"},
        labels={"rank": "Life Expectancy Rank", "year": "Year"}
    )
    
    # Invert y-axis so rank 1 is at the top
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        yaxis_title="Rank (1 = Highest Life Expectancy)",
        xaxis_title="Year"
    )
    
    # Apply highlighting if a country is selected
    if highlight_country:
        for trace in fig.data:
            if trace.name == highlight_country:
                trace.opacity = 1.0
                trace.line.width = 4  # Make highlighted line thicker
            else:
                trace.opacity = 0.3
                trace.line.width = 2
    
    return fig


@capture("graph")
def bar_chart(data_frame):
    data_2007 = data_frame[data_frame["year"] == 2007].sort_values("lifeExp", ascending=True)
    fig = px.bar(data_2007, y="country", x="lifeExp")

    return fig


########### Model code ############
dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            controls=[
                vm.Filter(column="year", selector=vm.RangeSlider(value=[1992, 2007])),
                vm.Parameter(
                    id="highlight_country_parameter",
                    targets=["bump_chart_with_highlighting.highlight_country"],
                    selector=vm.Dropdown(multi=False, options=selected_countries),
                ),
            ],
            components=[
                vm.Graph(
                    id="life_exp_bar_chart",
                    figure=bar_chart(data_frame=gapminder),
                    title="Life Expectancy Ranking (2007)",
                    actions=[
                        va.set_control(
                            type="set_control",
                            control="highlight_country_parameter",
                            value="y"
                        )
                    ],
                ),
                vm.Graph(
                    id="bump_chart_with_highlighting",
                    figure=bump_chart_with_highlighting(data_frame=gapminder),
                    title="Life Expectancy Ranking Changes Over Time",
                ),
            ],
            title="Southeast Asia Life Expectancy Dashboard",
        )
    ],
    title="Southeast Asia Development Trends",
)

app = Vizro().build(dashboard)
if __name__ == "__main__":
    app.run(debug=True, port=8050)
