"""This is a test app to test the dashboard layout."""

from vizro import Vizro
import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import export_data

iris = px.data.iris()

page = vm.Page(
    title="Buttons with an icon",
    layout=vm.Flex(),
    components=[
        vm.Button(
            icon="download",
            text="",
            description="Download the data!",
            variant="outlined",
            actions=[vm.Action(function=export_data())],
        ),
        vm.Graph(
            figure=px.scatter(
                iris,
                x="sepal_width",
                y="sepal_length",
                color="species",
                size="petal_length",
            ),
        ),
        vm.Button(
            text="View Data Source",
            href="https://www.kaggle.com/datasets/uciml/iris",
            icon="link",
            variant="outlined",
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
