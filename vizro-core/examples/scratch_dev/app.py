from vizro import Vizro
import vizro.models as vm
from vizro.models.types import capture
from dash import Input, Output, dcc, callback, ctx
import dash
import vizro.plotly.express as px

iris = px.data.iris()


@capture("action")
def my_custom_export():
    return dcc.send_data_frame(iris.to_csv, "mydf.csv")


@capture("action")
def my_custom_location(x=2):
    return f"/page-{x}"


# ------------------------- Page Build Components --------------------------

page_1 = vm.Page(
    title="Test page - Vizro actions",
    path="page-1",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
                ),
                vm.Button(
                    id="page_1_button_download",
                    text="Export data!",
                    actions=[
                        vm.Action(
                            function=my_custom_export(),
                            outputs=["vizro_download.data"],
                        )
                    ],
                ),
                vm.Button(
                    id="copy_page_1_button_download",
                    text="Copy Export data!",
                    actions=[
                        vm.Action(
                            function=my_custom_export(),
                            outputs=["vizro_download.data"],
                        )
                    ],
                ),
                vm.Button(
                    id="page_1_button_location",
                    text="Go to page 2!",
                    actions=[
                        vm.Action(
                            function=my_custom_location(),
                            outputs=["vizro_url.href"],
                        )
                    ],
                ),
                vm.Button(
                    id="copy_page_1_button_location",
                    text="Copy Go to page 2!",
                    actions=[
                        vm.Action(
                            function=my_custom_location(),
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
                    id="page_2_button_download",
                    text="Export data!",
                ),
                vm.Button(
                    id="copy_page_2_button_download",
                    text="Copy Export data!",
                ),
                vm.Button(
                    id="page_2_button_location",
                    text="Go to page 1!",
                ),
                vm.Button(
                    id="copy_page_2_button_location",
                    text="Copy Go to page 1!",
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


# --- Callbacks ---
# --- Download ---
@callback(
    Output("vizro_download", "data", allow_duplicate=True),
    Input("page_2_button_download", "n_clicks"),
    prevent_initial_call=True,
)
def export_callback(_):
    return dcc.send_data_frame(iris.to_csv, "mydf.csv")


@callback(
    Output("vizro_download", "data", allow_duplicate=True),
    Input("copy_page_2_button_download", "n_clicks"),
    prevent_initial_call=True,
)
def export_callback(_):
    return dcc.send_data_frame(iris.to_csv, "mydf.csv")


# --- Location ---
@callback(
    Output("vizro_url", "href", allow_duplicate=True),
    Input("page_2_button_location", "n_clicks"),
    prevent_initial_call=True,
)
def change_location_callback(_):
    return "/"


@callback(
    Output("vizro_url", "href", allow_duplicate=True),
    Input("copy_page_2_button_location", "n_clicks"),
    prevent_initial_call=True,
)
def change_location_callback(_):
    return "/"


# ------------------------- Dashboard Build Components -------------------------


page_3 = vm.Page(
    title="Test dashboard - Vizro actions",
    path="page-3",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
                ),
                vm.Button(
                    id="page_3_button_download",
                    text="Export data!",
                    actions=[
                        vm.Action(
                            function=my_custom_export(),
                            outputs=["dashboard_vizro_download.data"],
                        )
                    ],
                ),
                vm.Button(
                    id="copy_page_3_button_download",
                    text="Copy Export data!",
                    actions=[
                        vm.Action(
                            function=my_custom_export(),
                            outputs=["dashboard_vizro_download.data"],
                        )
                    ],
                ),
                vm.Button(
                    id="page_3_button_location",
                    text="Go to page 4!",
                    actions=[
                        vm.Action(
                            function=my_custom_location(x=4),
                            outputs=["dashboard_vizro_url.href"],
                        )
                    ],
                ),
                vm.Button(
                    id="copy_page_3_button_location",
                    text="Copy Go to page 4!",
                    actions=[
                        vm.Action(
                            function=my_custom_location(x=4),
                            outputs=["dashboard_vizro_url.href"],
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

page_4 = vm.Page(
    title="Test dashboard - pure Dash callbacks",
    path="page-4",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
                ),
                vm.Button(
                    id="page_4_button_download",
                    text="Export data!",
                ),
                vm.Button(
                    id="copy_page_4_button_download",
                    text="Copy Export data!",
                ),
                vm.Button(
                    id="page_4_button_location",
                    text="Go to page 3!",
                ),
                vm.Button(
                    id="copy_page_4_button_location",
                    text="Copy Go to page 3!",
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


# --- Callbacks ---
# --- Download ---
@callback(
    Output("dashboard_vizro_download", "data", allow_duplicate=True),
    Input("page_4_button_download", "n_clicks"),
    prevent_initial_call=True,
)
def export_callback(_):
    return dcc.send_data_frame(iris.to_csv, "mydf.csv")


@callback(
    Output("dashboard_vizro_download", "data", allow_duplicate=True),
    Input("copy_page_4_button_download", "n_clicks"),
    prevent_initial_call=True,
)
def export_callback(_):
    return dcc.send_data_frame(iris.to_csv, "mydf.csv")


# --- Location ---
@callback(
    Output("dashboard_vizro_url", "href", allow_duplicate=True),
    Input("page_4_button_location", "n_clicks"),
    prevent_initial_call=True,
)
def change_location_callback(_):
    return "/page-3"


@callback(
    Output("dashboard_vizro_url", "href", allow_duplicate=True),
    Input("copy_page_4_button_location", "n_clicks"),
    prevent_initial_call=True,
)
def change_location_callback(_):
    return "/page-3"


dashboard = vm.Dashboard(title="Test dashboard", pages=[page_1, page_2, page_3, page_4])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
