"""Dev App."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

first_page = vm.Page(
    title="First Page",
    components=[
        vm.Container(
            title="Container with info-icon visible",
            components=[
                vm.Graph(
                    figure=px.scatter(
                        iris,
                        x="sepal_length",
                        y="petal_width",
                        color="species",
                        custom_data=["species"],
                    ),
                ),
            ],
            description="test description",
            variant="outlined",
            collapsed=True,
        ),
    ],
    controls=[vm.Filter(column="species")],
)


second_page = vm.Page(
    title="Second Page",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    figure=px.scatter(
                        iris,
                        x="sepal_length",
                        y="petal_width",
                        color="species",
                        custom_data=["species"],
                    ),
                ),
            ],
            description="test description",
            variant="outlined",
        ),
    ],
)
dashboard = vm.Dashboard(pages=[first_page, second_page], navigation=vm.Navigation(nav_selector=vm.NavBar()))

if __name__ == "__main__":
    Vizro().build(dashboard).run()
