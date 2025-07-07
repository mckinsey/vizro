"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
from vizro.managers import data_manager


def dynamic_data_load(number_of_rows: int = 10):
    return px.data.iris().head(number_of_rows)


data_manager["static_df"] = dynamic_data_load(number_of_rows=150)
data_manager["dynamic_df"] = dynamic_data_load

static_sliders = vm.Page(
    title="Static sliders",
    components=[
        vm.Graph(figure=px.scatter("static_df", x="sepal_length", y="petal_length", color="species")),
    ],
    controls=[
        vm.Filter(column="sepal_length"),
        vm.Filter(column="petal_length", selector=vm.Slider()),
    ],
)


dynamic_sliders = vm.Page(
    title="Dynamic sliders",
    components=[
        vm.Graph(
            id="page_2_graph_1", figure=px.scatter("dynamic_df", x="sepal_length", y="petal_length", color="species")
        ),
    ],
    controls=[
        vm.Filter(column="sepal_length"),
        vm.Filter(column="petal_length", selector=vm.Slider()),
        vm.Parameter(
            targets=["page_2_graph_1.data_frame.number_of_rows"],
            selector=vm.Slider(
                title="Number of Rows",
                min=10,
                max=150,
            ),
        ),
    ],
)


url_dynamic_sliders = vm.Page(
    title="Dynamic data from URL",
    components=[
        vm.Graph(
            id="page_3_graph_1",
            figure=px.scatter("dynamic_df", x="sepal_length", y="petal_length", color="species"),
        )
    ],
    controls=[
        vm.Filter(column="sepal_length", show_in_url=True),
        vm.Filter(column="petal_length", selector=vm.Slider(), show_in_url=True),
        vm.Parameter(
            targets=["page_3_graph_1.data_frame.number_of_rows"],
            selector=vm.Slider(
                title="Number of Rows",
                min=10,
                max=150,
            ),
            show_in_url=True,
        ),
    ],
)

dashboard = vm.Dashboard(pages=[static_sliders, dynamic_sliders, url_dynamic_sliders])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
