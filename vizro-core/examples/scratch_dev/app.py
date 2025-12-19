from typing import Literal

import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro import Vizro
from vizro.managers import data_manager
from vizro.tables import dash_ag_grid

df = px.data.iris()
data_manager["iris"] = df

data_manager["gapminder_2007"] = px.data.gapminder().query("year == 2007")

gapminder = px.data.gapminder()
iris = px.data.iris()
tips = px.data.tips()


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

tab_1 = vm.Container(
    id="container_1",
    title="Tab I",
    components=[
        vm.Graph(
            figure=px.bar(
                "gapminder_2007",
                title="Graph 1",
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Graph(
            figure=px.box(
                "gapminder_2007",
                title="Graph 2",
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Graph(figure=px.scatter(iris, x="sepal_width", y="petal_length"), title="Title"),
        vm.AgGrid(figure=dash_ag_grid(data_frame=iris)),
    ],
)

tab_2 = vm.Container(
    id="container_2",
    title="Tab II",
    components=[
        vm.Graph(
            figure=px.scatter(
                "gapminder_2007",
                title="Graph 3",
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
    ],
)

tabs = vm.Page(
    id="page_1",
    title="Tabs",
    components=[vm.Tabs(id="tabs_1", tabs=[tab_1, tab_2])],
    controls=[vm.Filter(id="filter_1", column="continent")],
)

dashboard = vm.Dashboard(id="dashboard_1", pages=[tabs])

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
    app = Vizro().build(dashboard)
    # TODO: Do these tests elsewhere
    # for node in dashboard._tree:
    #     has_tree = hasattr(node.data, "_tree")
    #     if not has_tree:
    #         print(f"WARNING: {node.kind} (id={node.data.id}) missing ._tree attribute")
    # assert all(
    #     dashboard._tree[model.id].data is model
    #     for model in [dashboard] + dashboard.pages + [comp for page in dashboard.pages for comp in page.components]
    # )

    app.run()
