import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.tables import dash_ag_grid

df = px.data.iris()

page = vm.Page(
    title="Vizro on PyCafe",
    layout=vm.Flex(direction="row", wrap=True),
    components=[
        vm.Graph(
            id="scatter_chart",
            title="title one",
            figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", width=300),
        ),
        vm.Graph(
            id="hist_chart",
            title="title onetwothree",
            figure=px.histogram(df, x="sepal_width", color="species", width=300),
        ),
        vm.Graph(
            id="scatter_chart2", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", width=300)
        ),
        vm.Graph(id="hist_chart2", figure=px.histogram(df, x="sepal_width", color="species", width=300)),
    ],
    controls=[vm.Filter(column="species"), vm.Filter(column="petal_length"), vm.Filter(column="sepal_width")],
)

page_two = vm.Page(
    title="Tables",
    # layout=vm.Flex(direction="row", wrap=True),
    components=[
        vm.AgGrid(figure=dash_ag_grid(df), title="Table 1"),
        vm.AgGrid(figure=dash_ag_grid(df), title="Table 2 fd"),
        vm.AgGrid(figure=dash_ag_grid(df), title="Table 3 fdffdd"),
    ],
    controls=[vm.Filter(column="species"), vm.Filter(column="petal_length"), vm.Filter(column="sepal_width")],
)

dashboard = vm.Dashboard(pages=[page, page_two])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
