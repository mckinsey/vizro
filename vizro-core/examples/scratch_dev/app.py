import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

df = px.data.iris()

page = vm.Page(
    title="Vizro on PyCafe",
    layout=vm.Flex(direction="row"),
    components=[
        vm.Graph(
            id="scatter_chart",
            title="title one",
            figure=px.scatter(df, x="sepal_length", y="petal_width", color="species"),
        ),
        vm.Graph(id="hist_chart", title="title onetwothree", figure=px.histogram(df, x="sepal_width", color="species")),
        vm.Graph(id="scatter_chart2", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(id="hist_chart2", figure=px.histogram(df, x="sepal_width", color="species")),
        vm.Card(text="Placeholder text"),
    ],
    controls=[vm.Filter(column="species"), vm.Filter(column="petal_length"), vm.Filter(column="sepal_width")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
