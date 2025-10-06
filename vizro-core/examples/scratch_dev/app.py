"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro.models.types import capture
from vizro import Vizro
from vizro.tables import dash_ag_grid

# Filter to 2007 data and include all countries for better visualization
gapminder_2007 = px.data.gapminder().query("continent == 'Europe' and year == 2007")


@capture("graph")
def scatter_plot(data_frame, highlight_country=None):  # (1)!
    fig = px.scatter(
        data_frame,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        size_max=60,
        color="country",
        title="GDP per Capita vs Life Expectancy (2007)",
    )

    # Hide legend and set all points to low opacity by default
    fig.update_layout(showlegend=False)
    fig.update_traces(marker=dict(opacity=0.3, color="#00b4ff"))

    # Implement a highlighting logic for the scatter plot using the parameter value to identify which trace to visually highlight.
    for trace in fig.data:
        if trace.name == highlight_country:
            trace.marker.opacity = 1.0
            trace.marker.color = "#ff9222"
            trace.marker.line.width = 1
            trace.marker.line.color = "white"

    return fig


page = vm.Page(
    title="Cross-highlight from table to graph",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(data_frame=gapminder_2007),
            title="Click on a row to highlight that country in the scatter plot",
            actions=[va.set_control(control="highlight_parameter", value="country")],  # (6)!
        ),
        vm.Graph(
            id="scatter_chart",
            figure=scatter_plot(data_frame=gapminder_2007),
        ),
    ],
    controls=[
        vm.Parameter(
            id="highlight_parameter",
            targets=["scatter_chart.highlight_country"],
            selector=vm.Dropdown(multi=False, options=["None"] + gapminder_2007["country"].unique().tolist()),
            visible=False,
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
