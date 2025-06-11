from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from typing import Literal

gapminder_2007 = px.data.gapminder().query("year == 2007")


class CustomDashboard(vm.Dashboard):
    """Custom implementation of `Dashboard`."""

    type: Literal["custom_dashboard"] = "custom_dashboard"

    def _make_page_layout(self, *args, **kwargs):
        modal_with_button = html.Div(
            [
                dbc.Button("+ Add Entry", color="primary", id="open", n_clicks=0),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("New Entry")),
                        dbc.ModalBody(
                            # TODO - DB: options need to be replaced with database table
                            [
                                vm.Dropdown(options=["A", "B", "C"], title="Customer *", multi=False).build(),
                                vm.Dropdown(options=["A", "B", "C"], title="Category *", multi=False).build(),
                                vm.Dropdown(options=["A", "B", "C"], title="Region *", multi=False).build(),
                                vm.Dropdown(options=["A", "B", "C"], title="Status *", multi=False).build(),
                            ],
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button("Submit", id="close", className="ms-auto", n_clicks=0),
                            ]
                        ),
                    ],
                    id="modal",
                    is_open=False,
                ),
            ]
        )

        super_build_obj = super()._make_page_layout(*args, **kwargs)
        # We access the container with id="settings", where the theme switch is placed and add the H4.
        # You can see what's inside the settings.children container here: https://github.com/mckinsey/vizro/blob/main/vizro-core/src/vizro/models/_dashboard.py
        super_build_obj["settings"].children = [
            dbc.Button("↓ Export", color="secondary"),
            modal_with_button,
            super_build_obj["settings"].children,
        ]
        return super_build_obj


page_1 = vm.Page(
    title="Page with button",
    components=[
        vm.Graph(
            title="Graph 1",
            figure=px.bar(
                gapminder_2007,
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        )
    ],
)

dashboard = CustomDashboard(
    pages=[page_1],
)


@callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
