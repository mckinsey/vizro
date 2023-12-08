import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data
from vizro.models.types import capture
from time import sleep


@capture("action")
def my_custom_action(t: int):
    """Custom action."""
    sleep(t)


df = px.data.iris()

page = vm.Page(
    title="Example of a simple custom action",
    components=[
        vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Button(
            text="Export data",
            actions=[
                vm.Action(function=export_data()),
                vm.Action(function=my_custom_action(t=2)),
                vm.Action(function=export_data(file_format="xlsx")),
            ],
        ),
    ],
    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
