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
    title="Simple custom action",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Button(
            text="Export data",
            actions=[
                vm.Action(function=export_data()),
                vm.Action(function=my_custom_action(t=2)),
                vm.Action(function=export_data(file_format="xlsx")),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

# import vizro.plotly.express as px
# from vizro import Vizro
# import vizro.models as vm
#
# df = px.data.iris()
#
# page = vm.Page(
#     title="My first dashboard",
#     components=[
#         vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
#         vm.Graph(figure=px.histogram(df, x="sepal_width", color="species")),
#     ],
#     controls=[
#         vm.Filter(column="species"),
#     ],
# )
#
# dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
