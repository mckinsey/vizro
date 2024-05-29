import dash_ag_grid as dag
import pandas as pd
import vizro.models as vm
from asserts import assert_component_equal
from dash import dcc, html
from pandas import Timestamp
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

data = pd.DataFrame(
    {
        "cat": ["a", "b", "c"],
        "int": [4, 5, 6],
        "float": [7.3, 8.2, 9.1],
        "date": pd.to_datetime(["2021/01/01", "2021/01/02", "2021/01/03"]),
    }
)
column_defs = [{"field": "cat"}, {"field": "int"}, {"field": "float"}, {"field": "date"}]
row_data_date_converted = [
    {"cat": "a", "int": 4, "float": 7.3, "date": "2021-01-01"},
    {"cat": "b", "int": 5, "float": 8.2, "date": "2021-01-02"},
    {"cat": "c", "int": 6, "float": 9.1, "date": "2021-01-03"},
]
row_data_date_raw = [
    {"cat": "a", "date": Timestamp("2021-01-01 00:00:00"), "float": 7.3, "int": 4},
    {"cat": "b", "date": Timestamp("2021-01-02 00:00:00"), "float": 8.2, "int": 5},
    {"cat": "c", "date": Timestamp("2021-01-03 00:00:00"), "float": 9.1, "int": 6},
]
default_col_defs = {
    "filter": True,
    "filterParams": {"buttons": ["apply", "reset"], "closeOnApply": True},
    "resizable": True,
    "sortable": True,
}
style = {"height": "100%"}


class TestDashAgGrid:
    def test_dash_ag_grid(self):
        grid = dash_ag_grid(data_frame=data)()
        assert_component_equal(
            grid,
            dag.AgGrid(
                columnDefs=column_defs,
                rowData=row_data_date_converted,
                defaultColDef=default_col_defs,
                style=style,
            ),
            keys_to_strip={"className", "dashGridOptions"},
        )
        # skipping only dashGridOptions as this is mostly our defaults for data formats, and would crowd the tests


class TestCustomDashAgGrid:
    def test_custom_dash_ag_grid(self):
        """Tests whether a custom created grid callable can be correctly be built in vm.AgGrid."""
        id = "custom_ag_grid"

        @capture("ag_grid")
        def custom_ag_grid(data_frame):
            return dag.AgGrid(
                columnDefs=[{"field": col} for col in data_frame.columns],
                rowData=data_frame.to_dict("records"),
            )

        grid_model = vm.AgGrid(
            id=id,
            figure=custom_ag_grid(data_frame=data),
        )
        grid_model.pre_build()
        custom_grid = grid_model.build()

        expected_grid = dcc.Loading(
            [
                None,
                html.Div(
                    dag.AgGrid(id="__input_custom_ag_grid", columnDefs=column_defs, rowData=row_data_date_raw),
                    id=id,
                    className="table-container",
                ),
            ],
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(custom_grid, expected_grid)

    def test_custom_dash_ag_grid_column_referral(self):
        """Tests whether a custom created grid can be correctly built in vm.AgGrid.

        This test focuses on the case that the custom grid includes column referrals on presumed data knowledge.
        """
        id = "custom_ag_grid"

        @capture("ag_grid")
        def custom_ag_grid(data_frame):
            data_frame["cat"]  # access "existing" column
            return dag.AgGrid(
                columnDefs=[{"field": col} for col in data_frame.columns],
                rowData=data_frame.to_dict("records"),
            )

        grid_model = vm.AgGrid(
            id=id,
            figure=custom_ag_grid(data_frame=data),
        )
        grid_model.pre_build()
        custom_grid = grid_model.build()

        expected_grid = dcc.Loading(
            [
                None,
                html.Div(
                    dag.AgGrid(id="__input_custom_ag_grid", columnDefs=column_defs, rowData=row_data_date_raw),
                    id=id,
                    className="table-container",
                ),
            ],
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(custom_grid, expected_grid)
