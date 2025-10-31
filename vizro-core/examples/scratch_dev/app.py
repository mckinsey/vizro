"""Dev app to try things out."""

from typing import Literal

import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro import Vizro
from vizro.managers import data_manager

df = px.data.iris()
data_manager["iris"] = df


# 2. Create new custom component
class Jumbotron(vm.VizroBaseModel):
    """New custom component `Jumbotron`."""

    type: Literal["custom_component"] = "custom_component"
    title: str
    subtitle: str
    text: str

    def build(self):
        """Build the new component based on Dash components."""
        return html.Div([html.H2(self.title), html.H3(self.subtitle), html.P(self.text)])


class CustomCard(vm.VizroBaseModel):
    """New custom component `Card`."""

    type: Literal["custom_component"] = "custom_component"
    title: str
    description: str

    def build(self):
        """Build the new component based on Dash components."""
        return html.Div(
            [
                html.Div(
                    [
                        html.H4(self.title, style={"margin": "0 0 10px 0"}),
                        html.P(self.description, style={"margin": "0"}),
                    ],
                    style={
                        "border": "1px solid #ddd",
                        "border-radius": "8px",
                        "padding": "16px",
                        "background-color": "#f9f9f9",
                    },
                )
            ]
        )


page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(figure=px.histogram(df, x="sepal_width", color="species")),
        Jumbotron(
            title="Custom component",
            subtitle="This is a subtitle",
            text="This is the main body of text of the Jumbotron.",
        ),
        Jumbotron(
            title="Custom component 2",
            subtitle="This is a subtitle",
            text="This is the main body of text of the Jumbotron.",
        ),
        CustomCard(
            title="Custom card",
            description="This is a description of the custom card.",
        ),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

# Same configuration as JSON
# dashboard_config = {
#     "type": "dashboard",
#     "pages": [
#         {
#             "type": "page",
#             "title": "My first dashboard",
#             "components": [
#                 {
#                     "type": "graph",
#                     "figure": {
#                         "_target_": "scatter",
#                         "data_frame": "iris",
#                         "x": "sepal_length",
#                         "y": "petal_width",
#                         "color": "species",
#                     },
#                 },
#                 {
#                     "type": "graph",
#                     "figure": {
#                         "_target_": "histogram",
#                         "data_frame": "iris",
#                         "x": "sepal_width",
#                         "color": "species",
#                     },
#                 },
#             ],
#             "controls": [
#                 {
#                     "type": "filter",
#                     "column": "species",
#                 }
#             ],
#         }
#     ],
# }

# dashboard = vm.Dashboard.model_validate(dashboard_config)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
