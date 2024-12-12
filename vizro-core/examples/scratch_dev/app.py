"""Dev app to try things out."""

from vizro import Vizro
import vizro.models as vm
import vizro.plotly.express as px
from dash import Input, Output, State, callback
from vizro.tables import dash_ag_grid


df = px.data.gapminder()
gapminder_data = (
    df.groupby(by=["continent", "year"]).agg({"lifeExp": "mean", "pop": "sum", "gdpPercap": "mean"}).reset_index()
)
first_page = vm.Page(
    title="First Page",
    layout=vm.Layout(grid=[[0, 0], [1, 1], [1, 1], [1, 1]]),
    components=[
        vm.Card(
            text="""
                # First dashboard page
                This pages shows the inclusion of markdown text in a page and how components
                can be structured using Layout.
            """,
        ),
        vm.AgGrid(
            figure=dash_ag_grid(data_frame=gapminder_data, dashGridOptions={"pagination": True}),
            title="Gapminder Data Insights",
            header="""#### An Interactive Exploration of Global Health, Wealth, and Population""",
            footer="""SOURCE: **Plotly gapminder data set, 2024**""",
        )
    ],
    controls=[
        vm.Filter(column="continent", selector=vm.Checklist(id="test")),
        # vm.Filter(column="continent"),
    ],
)

dashboard = vm.Dashboard(pages=[first_page])


@callback(
    [Output("test", "value"), Output("test-select-all", "value")],
    [Input("test-select-all", "value"), Input("test", "value")],
    State("test", "options"),
)
def update_checklist(value_1, value_2, options):
    if value_1:
        if len(value_2) == 0:
            return options, value_1
        if len(value_2) != len(options):
            return value_2, []
    else:
        if len(value_2) == len(options):
            return options, ["Select All"]



if __name__ == "__main__":
    Vizro().build(dashboard).run()
