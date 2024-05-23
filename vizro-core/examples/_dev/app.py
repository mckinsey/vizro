import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager


def load_iris_data(number_of_points=10):
    iris = px.data.iris()
    return iris.sample(number_of_points)


data_manager["iris"] = load_iris_data

page = vm.Page(
    title="Update the chart on page refresh",
    components=[vm.Graph(id="graph", figure=px.box("iris", x="species", y="petal_width", color="species"))],
    controls=[
        vm.Parameter(
            targets=["graph.data_frame.number_of_points"], selector=vm.Slider(min=1, max=20, step=1, value=10)
        ),
        vm.Filter(column="species"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
