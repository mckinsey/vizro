"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

df = px.data.gapminder()
df_aggregated = (
    df.groupby(by=["continent", "year"]).agg({"lifeExp": "mean", "pop": "sum", "gdpPercap": "mean"}).reset_index()
)

page_aggrid = vm.Page(
    title="Ag Grid and Graph",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.AgGrid(
            title="Graph Title",
            figure=dash_ag_grid(df),
        ),
        vm.Graph(
            figure=px.box(
                df_aggregated,
                x="continent",
                y="lifeExp",
                color="continent",
                labels={"lifeExp": "Life Expectancy", "continent": "Continent"},
                title="Graph Title",
            ),
        ),
    ],
)

page_data_table = vm.Page(
    title="Data Table and Graph",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.Table(
            title="Graph Title",
            figure=dash_data_table(df),
        ),
        vm.Graph(
            figure=px.box(
                df_aggregated,
                x="continent",
                y="lifeExp",
                color="continent",
                labels={"lifeExp": "Life Expectancy", "continent": "Continent"},
                title="Graph Title",
            ),
        ),
    ],
)


dashboard = vm.Dashboard(pages=[page_aggrid, page_data_table])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
