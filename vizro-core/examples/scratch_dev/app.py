"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro.models.types import capture
from vizro import Vizro
from vizro.tables import dash_ag_grid

gapminder = px.data.gapminder().query("continent == 'Europe' and year == 2007")


@capture("graph")
def scatter_with_highlight(data_frame, highlight_country=None):
    country_is_highlighted = data_frame["country"] == highlight_country
    fig = px.scatter(
        data_frame,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        size_max=60,
        opacity=0.3,
        color=country_is_highlighted,
        category_orders={"color": [False, True]},
    )

    if highlight_country is not None:
        fig.update_traces(selector=1, marker={"line_width": 2, "opacity": 1})

    fig.update_layout(showlegend=False)
    return fig


page = vm.Page(
    title="Cross-highlight from table",
    layout=vm.Grid(grid=[[0, 1]], col_gap="80px"),
    components=[
        vm.AgGrid(
            header="💡 Click on a row to highlight that country in the scatter plot",
            figure=dash_ag_grid(data_frame=gapminder),
            actions=va.set_control(control="highlight_parameter", value="country"),
        ),
        vm.Graph(
            id="scatter_chart",
            figure=scatter_with_highlight(gapminder),
        ),
    ],
    controls=[
        vm.Parameter(
            id="highlight_parameter",
            targets=["scatter_chart.highlight_country"],
            selector=vm.RadioItems(options=["NONE", *gapminder["country"]]),
            visible=False,
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=False)
