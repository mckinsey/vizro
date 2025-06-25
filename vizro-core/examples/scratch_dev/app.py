from vizro import Vizro
import vizro.models as vm
import vizro.plotly.express as px
from vizro.models.types import capture
from dash import Input, Output, dcc, callback, ctx
import dash

iris = px.data.iris()


@capture("action")
def my_custom_export(n_clicks):
    if n_clicks:
        return dcc.send_data_frame(iris.to_csv, "mydf.csv")


@capture("action")
def my_custom_location(n_clicks):
    if n_clicks:
        return "/page-2"


page_1 = vm.Page(
    title="Test page - Vizro actions",
    path="page-1",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
                ),
                vm.Graph(
                    id="graph",
                    figure=px.bar(
                        iris,
                        x="sepal_length",
                        y="sepal_width",
                        color="species",
                        title="Container I - Bar",
                    ),
                ),
                vm.Button(
                    id="button_download",
                    text="Export data!",
                    actions=[
                        vm.Action(
                            function=my_custom_export(),
                            inputs=["button_download.n_clicks"],
                            outputs=["vizro_download.data"],
                        )
                    ],
                ),
                vm.Button(
                    id="button_location",
                    text="Go to page 2!",
                    actions=[
                        vm.Action(
                            function=my_custom_location(),
                            inputs=["button_location.n_clicks"],
                            outputs=["vizro_url.href"],
                        )
                    ],
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
        )
    ],
)

page_2 = vm.Page(
    title="Test page - pure Dash callbacks",
    path="page-2",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
                ),
                vm.Button(
                    id="button_download_2",
                    text="Export data!",
                ),
                vm.Button(
                    id="button_location_2",
                    text="Go to page 1!",
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
        )
    ],
)


@callback(
    Output("vizro_url", "href", allow_duplicate=True),
    Input("button_location_2", "n_clicks"),
    prevent_initial_call="initial_duplicate",
)
def change_location_callback(n_clicks):
    if ctx.triggered_id == "button_location_2":
        return "/"
    else:
        raise dash.exceptions.PreventUpdate


@callback(
    Output("vizro_download", "data", allow_duplicate=True),
    Input("button_download_2", "n_clicks"),
    prevent_initial_call="initial_duplicate",
)
def export_callback(n_clicks):
    if ctx.triggered_id == "button_download_2":
        return dcc.send_data_frame(iris.to_csv, "mydf.csv")
    else:
        raise dash.exceptions.PreventUpdate


# @callback(
#     Output("vizro_url", "href", allow_duplicate=True),
#     Input("button_location", "n_clicks"),
#     prevent_initial_call='initial_duplicate'
# )
# def change_location_callback1(n_clicks):
#     if ctx.triggered_id == "button_location":
#         return "/page-2"
#     else:
#         raise dash.exceptions.PreventUpdate
#
#
# @callback(
#     Output("vizro_download", "data", allow_duplicate=True),
#     Input("button_download", "n_clicks"),
#     prevent_initial_call='initial_duplicate'
# )
# def export_callback1(n_clicks):
#     if ctx.triggered_id == "button_download":
#         return dcc.send_data_frame(iris.to_csv, "mydf.csv")
#     else:
#         raise dash.exceptions.PreventUpdate
#


dashboard = vm.Dashboard(title="Test dashboard", pages=[page_1, page_2])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
