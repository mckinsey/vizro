"""Dev app to try things out."""

""" FOR REVIEWERS:
To reproduce the bug on the main:
1. Open the first page
2. Set the number of rows to 150 (bottom slider)
3. Select ["setosa", "versicolor"] in the multi-select dropdown
4. Select "versicolor" in the single-select dropdown
5. Refresh the page -> The value is unexpectedly reset to "setosa" in the multi-select dropdown and clear
   in the single-select dropdown. The value should remain the same as it was before the refresh.
"""

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
from vizro.managers import data_manager


SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}


data_manager["dynamic_df"] = lambda number_of_rows=10: px.data.iris().head(number_of_rows)

dropdown_dynamic_data_bug = vm.Page(
    title="Dropdown dynamic data bug",
    components=[
        vm.Graph(
            id="page_1_graph",
            figure=px.scatter(
                "dynamic_df", x="sepal_length", y="petal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(title="Multi-select dropdown", description="Select species")),
        vm.Filter(
            column="species",
            selector=vm.Dropdown(multi=False, title="Single-select dropdown", description="Select species"),
        ),
        vm.Parameter(
            targets=["page_1_graph.data_frame.number_of_rows"],
            selector=vm.Slider(
                title="Number of Rows",
                min=10,
                max=150,
            ),
        ),
    ],
)

dropdown_preset_value = vm.Page(
    title="Dropdown preset value",
    components=[
        vm.Graph(
            id="page_2_graph",
            figure=px.scatter(
                "dynamic_df", x="sepal_length", y="petal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["setosa", "versicolor"])),
        vm.Filter(
            column="species",
            selector=vm.Dropdown(multi=False, value="versicolor"),
        ),
        vm.Parameter(
            targets=["page_2_graph.data_frame.number_of_rows"],
            selector=vm.Slider(
                title="Number of Rows",
                min=10,
                max=150,
            ),
        ),
    ],
)

dropdown_url = vm.Page(
    title="Dropdown in URL",
    components=[
        vm.Graph(
            id="page_3_graph",
            figure=px.scatter(
                "dynamic_df", x="sepal_length", y="petal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
    ],
    controls=[
        vm.Filter(
            id="page_3_filter_1",
            show_in_url=True,
            column="species",
        ),
        vm.Filter(
            id="page_3_filter_2",
            show_in_url=True,
            column="species",
            selector=vm.Dropdown(multi=False),
        ),
        vm.Parameter(
            targets=["page_3_graph.data_frame.number_of_rows"],
            selector=vm.Slider(
                title="Number of Rows",
                min=10,
                max=150,
            ),
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[
        dropdown_dynamic_data_bug,
        dropdown_preset_value,
        dropdown_url,
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
