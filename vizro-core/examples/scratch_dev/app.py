import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.iris()

page = vm.Page(
    title="My first page",
    layout=vm.Flex(),  # (1)!
    components=[
        vm.Graph(figure=px.histogram(df, x="sepal_length")),
        vm.Button(text="Export data", actions=va.export_data()),
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
