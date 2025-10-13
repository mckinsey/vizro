"""Scratch app"""

from typing import Literal

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro import Vizro

df = px.data.iris()


# 2. Create new custom component
class Jumbotron(vm.VizroBaseModel):
    """New custom component `Jumbotron`."""

    type: Literal["jumbotron"] = "jumbotron"
    title: str
    subtitle: str
    text: str

    def build(self):
        """Build the new component based on Dash components."""
        return html.Div([html.H2(self.title), html.H3(self.subtitle), html.P(self.text)])


# vm.Page.add_type("components", Jumbotron)
# print("--------------------------------")


class TooltipNonCrossRangeSlider(vm.RangeSlider):
    """Custom numeric multi-selector `TooltipNonCrossRangeSlider`."""

    type: Literal["other_range_slider"] = "other_range_slider"

    def build(self):
        """Extend existing component by calling the super build and update properties."""
        range_slider_build_obj = super().build()
        range_slider_build_obj[self.id].allowCross = False
        range_slider_build_obj[self.id].tooltip = {"always_visible": True, "placement": "bottom"}
        return range_slider_build_obj


print("----Adding to Filter----")
vm.Filter.add_type("selector", TooltipNonCrossRangeSlider)
print("----Adding to Parameter----")
vm.Parameter.add_type("selector", TooltipNonCrossRangeSlider)
print("--------------------------------")

# First page
page1 = vm.Page(
    title="My first page",
    components=[
        # Jumbotron(
        #     title="Custom component based on new creation",
        #     subtitle="This is a subtitle to summarize some content.",
        #     text="This is the main body of text of the Jumbotron.",
        # ),
        vm.Graph(
            id="graph_1",
            figure=px.scatter_matrix(
                df,
                dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"],
                color="species",
                opacity=0.5,
            ),
        ),
    ],
    controls=[
        vm.Filter(column="sepal_length", selector=TooltipNonCrossRangeSlider(id="filter_1")),
        vm.Parameter(targets=["graph_1.opacity"], selector=TooltipNonCrossRangeSlider(id="parameter_1")),
    ],
)

# page_close = vm.Page.model_validate(page1)

# # Second page with two graphs
# page2 = vm.Page(
#     title="My second page",
#     components=[
#         vm.Graph(
#             figure=px.scatter_matrix(
#                 df, dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"], color="species"
#             ),
#         ),
#         vm.Graph(
#             figure=px.scatter(df, x="sepal_length", y="sepal_width", color="species", size="petal_width"),
#         ),
#     ],
# )
# So I think the answer is that we need to rebuild also the outer model!
# Not quite sure why this worked before!
# Additional note: would that have solved the issue on the Vizro MCP server with CapturedCallables?
# vm.Dashboard.model_rebuild(force=True)


dashboard = vm.Dashboard(pages=[page1])

# dashboard_config = {
#     "pages": [
#         {
#             "id": "page_1",
#             "title": "My first page",
#             "components": [
#                 {
#                     "type": "graph",
#                     "id": "graph_1",
#                     "figure": {
#                         "_target_": "scatter_matrix",
#                         "data_frame": "iris",
#                         "dimensions": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
#                         "color": "species",
#                     },
#                 }
#             ],
#         },
#         {
#             "id": "page_2",
#             "title": "My second page",
#             "components": [
#                 {
#                     "type": "graph",
#                     "id": "graph_2",
#                     "figure": {
#                         "_target_": "scatter_matrix",
#                         "data_frame": "iris",
#                         "dimensions": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
#                         "color": "species",
#                     },
#                 },
#                 {
#                     "type": "graph",
#                     "id": "graph_3",
#                     "figure": {
#                         "_target_": "scatter",
#                         "data_frame": "iris",
#                         "x": "sepal_length",
#                         "y": "sepal_width",
#                         "color": "species",
#                         "size": "petal_width",
#                     },
#                 },
#             ],
#         },
#     ],
# }

# Still requires a .py to add data to the data manager and parse YAML configuration
# See yaml_version example


if __name__ == "__main__":
    from vizro.managers import model_manager

    # print("=== START ===")
    # Create dashboard from config
    # dashboard_from_config = vm.Dashboard.model_validate(dashboard_config, context={"build_tree": True})
    # dashboard_config = vm.Dashboard(**dashboard_config)  # this line is necessary for yaml/json config of dashboard
    # What if we want to directly add model to build? ==> instantiate first, then build? That works, see code in _vizro.py
    # app = Vizro().build(dashboard)
    # dashboard_from_config._tree.print(repr=lambda node: f"{node.kind}: {node.data.__class__.__name__}: {node.data.id}")
    # model_manager.print_dashboard_tree()

    print(
        "Container Filter   ",
        vm.Container.model_json_schema()["$defs"]["Filter"]["properties"]["selector"]["anyOf"][0]["oneOf"][-2:],
    )
    print(
        "Container Parameter",
        vm.Container.model_json_schema()["$defs"]["Parameter"]["properties"]["selector"]["oneOf"][-2:],
    )

    print(
        "Page Filter        ",
        vm.Page.model_json_schema()["$defs"]["Filter"]["properties"]["selector"]["anyOf"][0]["oneOf"][-2:],
    )
    print(
        "Page Parameter     ",
        vm.Page.model_json_schema()["$defs"]["Parameter"]["properties"]["selector"]["oneOf"][-2:],
    )
    print(
        "Tabs  Filter       ",
        vm.Tabs.model_json_schema()["$defs"]["Filter"]["properties"]["selector"]["anyOf"][0]["oneOf"][-2:],
    )
    print(
        "Tabs  Parameter    ",
        vm.Tabs.model_json_schema()["$defs"]["Parameter"]["properties"]["selector"]["oneOf"][-2:],
    )
    print(
        "Dashboard Filter   ",
        vm.Dashboard.model_json_schema()["$defs"]["Filter"]["properties"]["selector"]["anyOf"][0]["oneOf"][-2:],
    )
    print(
        "Dashboard Parameter",
        vm.Dashboard.model_json_schema()["$defs"]["Parameter"]["properties"]["selector"]["oneOf"][-2:],
    )
    print("================================================")
    # assert vm.Dashboard.model_json_schema()["$defs"]["Filter"] == vm.Container.model_json_schema()["$defs"]["Filter"]
