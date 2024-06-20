"""Example to show dashboard configuration."""
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.actions import filter_interaction


def load_data(points=0):
    return px.data.iris().head(points)


data_manager['my_data'] = load_data
graph_config = dict(x="sepal_length", y="petal_width", color="species")


page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter('my_data', **graph_config)
        ),
        vm.Graph(
            id="scatter_chart_2",
            figure=px.scatter(px.data.iris().tail(50), custom_data=["species"], **graph_config),
            actions=[
                vm.Action(
                    function=filter_interaction(targets=["scatter_chart_3"]),
                )
            ]
        ),
        vm.Graph(
            id="scatter_chart_3",
            figure=px.scatter(px.data.iris(), **graph_config),
        ),
    ],
    controls=[
        vm.Filter(column="species", targets=["scatter_chart", "scatter_chart_2"]),
        vm.Parameter(
            targets=['scatter_chart.data_frame.points'],
            selector=vm.Slider(
                id="parameter_points",
                min=0,
                max=150,
                step=10,
            )
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=False)
