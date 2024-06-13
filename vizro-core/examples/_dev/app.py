"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

df = px.data.gapminder()

page_one = vm.Page(
    title="Dash AG Grid",
    layout=vm.Layout(grid=[[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]], col_gap="0px"),
    components=[
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
    ],
    controls=[
        vm.Filter(column="continent")
    ]
)

page_two = vm.Page(
    title="Dash Data Table",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.Table(title="Equal Title One", figure=dash_data_table(data_frame=df)),
        vm.Graph(figure=px.box(df, x="continent", y="lifeExp", title="Equal Title One")),
    ],
    controls=[
        vm.Filter(column="continent")
    ]
)
dashboard = vm.Dashboard(pages=[page_one, page_two], theme="vizro_light")


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=False)
