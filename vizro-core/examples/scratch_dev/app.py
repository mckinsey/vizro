"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro.models.types import capture
from vizro import Vizro
from vizro.tables import dash_ag_grid

selected_countries = [
    "Singapore",
    "Malaysia",
    "Thailand",
    "Indonesia",
    "Philippines",
    "Vietnam",
    "Cambodia",
    "Myanmar",
]

gapminder = px.data.gapminder().query("country.isin(@selected_countries)")


@capture("graph")
def bar_with_highlight(data_frame, highlight_country=None):
    country_is_highlighted = data_frame["country"] == highlight_country
    fig = px.bar(
        data_frame,
        x="lifeExp",
        y="country",
        labels={"lifeExp": "lifeExp in 2007"},
        color=country_is_highlighted,
        category_orders={"country": sorted(data_frame["country"])},
    )
    fig.update_layout(showlegend=False)
    return fig


page = vm.Page(
    title="Self-highlight a graph and cross-filter",
    components=[
        vm.Graph(
            id="bar_chart",
            figure=bar_with_highlight(gapminder.query("year == 2007")),
            header="💡 Click on a bar to highlight the selected country and filter the table below",
            actions=[
                va.set_control(control="highlight_parameter", value="y"),
                va.set_control(control="country_filter", value="y"),
            ],
        ),
        vm.AgGrid(id="gapminder_table", figure=dash_ag_grid(data_frame=gapminder)),
    ],
    controls=[
        vm.Parameter(
            id="highlight_parameter",
            targets=["bar_chart.highlight_country"],
            selector=vm.RadioItems(options=["NONE", *gapminder["country"]]),
            visible=False,
        ),
        vm.Filter(id="country_filter", column="country", targets=["gapminder_table"], visible=False),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
