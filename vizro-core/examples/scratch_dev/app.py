from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from typing import Literal
from vizro.tables import dash_ag_grid, dash_data_table
from vizro.figures import kpi_card_reference, kpi_card
import pandas as pd
import dash_bootstrap_components as dbc


gapminder_2007 = px.data.gapminder().query("year == 2007")
kpi_df = pd.DataFrame(
    [[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]],
    columns=["Actual", "Reference", "Category"],
)


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
                                vm.Dropdown(options=["A", "B", "C"], title="Category *").build(),
                                vm.Dropdown(options=["A", "B", "C"], title="Region *", multi=False).build(),
                                vm.Dropdown(options=["A", "B", "C"], title="Status *", multi=False).build(),
                            ],
                            style={"display": "flex", "flex-direction": "column", "gap": "1rem"},
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
            ],
        )

        super_build_obj = super()._make_page_layout(*args, **kwargs)
        # We access the container with id="settings", where the theme switch is placed and add the H4.
        # You can see what's inside the settings.children container here: https://github.com/mckinsey/vizro/blob/main/vizro-core/src/vizro/models/_dashboard.py
        super_build_obj["settings"].children = [
            modal_with_button,
            super_build_obj["settings"].children,
        ]
        return super_build_obj


page_1 = vm.Page(
    title="Page with modal",
    components=[
        vm.Table(figure=dash_data_table(gapminder_2007)),
    ],
    controls=[vm.Filter(column="continent"), vm.Filter(column="country")],
)


page_2 = vm.Page(
    title="kpi-indicators-page",
    layout=vm.Grid(grid=[[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, -1]]),
    components=[
        # Style 1: Value Only
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                title="Value I",
                agg_func="sum",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                title="Value II",
                agg_func="mean",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                title="Value III",
                agg_func="median",
            )
        ),
        # Style 2: Value and reference value
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Reference",
                reference_column="Actual",
                title="Ref. Value II",
                agg_func="sum",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Actual",
                reference_column="Reference",
                title="Ref. Value I",
                agg_func="sum",
            )
        ),
        vm.Figure(
            id="kpi-card-reverse-coloring",
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Actual",
                reference_column="Reference",
                title="Ref. Value III",
                agg_func="median",
                icon="shopping_cart",
            ),
        ),
        # Style 3: Value and icon
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                icon="shopping_cart",
                title="Icon I",
                agg_func="sum",
                value_format="${value:.2f}",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                icon="payment",
                title="Icon II",
                agg_func="mean",
                value_format="{value:.0f}€",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                icon="monitoring",
                title="Icon III",
                agg_func="median",
            )
        ),
        # Style 4: Reference value and reverse coloring
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Actual",
                reference_column="Reference",
                title="Ref. Value (pos-reverse)",
                reverse_color=True,
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Reference",
                reference_column="Actual",
                title="Ref. Value (neg-reverse)",
                reverse_color=True,
            ),
        ),
    ],
    controls=[vm.Filter(column="Category", selector=vm.Dropdown(id="dropdown-filter"))],
)

page_3 = vm.Page(title="datepicker-page", components=[vm.Text(text="Placeholder")])


@callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


dashboard = CustomDashboard(
    pages=[page_1, page_2, page_3],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Data", pages=["Page with modal"], icon="database"),
                vm.NavLink(label="Charts", pages=["kpi-indicators-page", "datepicker-page"], icon="bar_chart"),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro(external_stylesheets=[dbc.themes.BOOTSTRAP]).build(dashboard).run()
