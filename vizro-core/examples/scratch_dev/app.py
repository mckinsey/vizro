import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro

df = px.data.iris()

page_1 = vm.Page(
    title="BUG theme switch doesn't work with Flex layout",
    layout=vm.Flex(),
    components=[
        vm.Graph(figure=px.scatter(data_frame=df, x="sepal_width", y="sepal_length")),
        vm.Graph(figure=px.scatter(data_frame=df.head(10), x="sepal_width", y="sepal_length")),
        vm.Card(text="test"),
    ],
)

dashboard = vm.Dashboard(pages=[page_1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
