"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from components import CollapsibleContainer, FlexContainer
from dash import Input, Output, clientside_callback

vm.Page.add_type("components", FlexContainer)
FlexContainer.add_type("components", CollapsibleContainer)

vm.Page.add_type("components", CollapsibleContainer)


iris = px.data.iris()


page = vm.Page(
    title="Collapse containers with flex container",
    components=[
        FlexContainer(
            components=[
                CollapsibleContainer(
                    id="collapsible-container",
                    title="Collapsible container",
                    components=[
                        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                        vm.Graph(figure=px.histogram(iris, x="sepal_width", color="species")),
                        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                    ],
                    layout=vm.Layout(grid=[[0, 0, 0, 0], [1, 1, 2, 2]]),
                ),
                vm.Container(
                    title="Regular container",
                    components=[vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"))],
                ),
            ]
        )
    ],
)


dashboard = vm.Dashboard(pages=[page])

clientside_callback(
    """
    (n_clicks) => {
       if (n_clicks % 2 === 1) {
        return [true, {transform: "rotate(180deg)", transition: "transform 0.35s ease-in-out"}];
    } else return [false, {transform: "rotate(0deg)", transition: "transform 0.35s ease-in-out"}];
    }
    """,
    [Output("collapsible-container", "is_open"), Output("collapsible-container_icon", "style")],
    Input("collapsible-container_title", "n_clicks"),
)


if __name__ == "__main__":
    Vizro().build(dashboard).run()
