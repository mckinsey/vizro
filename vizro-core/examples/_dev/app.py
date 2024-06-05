"""Example to show dashboard configuration."""


# TODO: Return an empty graph from parameter action if data_frame function argument in targeted.
# TODO: Implement a logic to pass certain kwargs to certain data sources
# TODO: move clientside callbacks to slider/range_slider pre_build method or something similar.


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
                value=70
            )
        ),
    ],
)

# TODO: Consider adding a new Dashboard argument called `components`, where any dash component could be added to
#  the global container.
dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    from dash import Input, Output, dcc, callback

    app = Vizro(
        routing_callback_inputs={
            "points": Input("parameter_points_store", "data"),
        }
    )

    app.build(dashboard)

    app.dash.layout.children.append(dcc.Store(id="parameter_points_store", data=0))

    @callback(
        Output("parameter_points_store", "data"),
        Input("parameter_points", "value")
    )
    def update_parameter_points_store(value):
        # from time import sleep
        # sleep(0.5)
        return value

    app.run()
