import pandas as pd
import vizro.models as vm
from asserts import assert_component_equal
from dash import dash_table, dcc, html
from vizro.models.types import capture
from vizro.tables import dash_data_table

data = pd.DataFrame(
    {
        "cat": ["a", "b", "c"],
        "int": [4, 5, 6],
        "float": [7.3, 8.2, 9.1],
        "date": pd.to_datetime(["2021/01/01", "2021/01/02", "2021/01/03"]),
    }
)
columns = [
    {"id": "cat", "name": "cat"},
    {"id": "int", "name": "int"},
    {"id": "float", "name": "float"},
    {"id": "date", "name": "date"},
]
data_in_table = [
    {"cat": "a", "int": 4, "float": 7.3, "date": pd.Timestamp("2021-01-01 00:00:00")},
    {"cat": "b", "int": 5, "float": 8.2, "date": pd.Timestamp("2021-01-02 00:00:00")},
    {"cat": "c", "int": 6, "float": 9.1, "date": pd.Timestamp("2021-01-03 00:00:00")},
]


class TestDashDataTable:
    def test_dash_data_table(self):
        table = dash_data_table(data_frame=data)()
        assert_component_equal(
            table,
            dash_table.DataTable(
                columns=columns,
                data=data_in_table,
                style_as_list_view=True,
                style_cell={"position": "static"},
                style_data={"border_bottom": "1px solid var(--border-subtle-alpha-01)", "height": "40px"},
                style_header={
                    "border_bottom": "1px solid var(--state-overlays-selected-hover)",
                    "border_top": "1px solid var(--main-container-bg-color)",
                    "height": "32px",
                },
                style_data_conditional=[
                    {
                        "if": {"state": "active"},
                        "backgroundColor": "var(--state-overlays-selected)",
                        "border": "1px solid var(--state-overlays-selected)",
                    }
                ],
            ),
        )


class TestCustomDashDataTable:
    def test_custom_dash_data_table(self):
        """Tests whether a custom created table callable can be correctly be built in vm.Table."""
        id = "custom_dash_data_table"

        @capture("table")
        def custom_dash_data_table(data_frame):
            return dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in data_frame.columns],
                data=data_frame.to_dict("records"),
            )

        table = vm.Table(
            id=id,
            figure=custom_dash_data_table(data_frame=data),
        )
        table.pre_build()

        custom_table = table.build()

        expected_table_object = dash_table.DataTable(
            columns=columns,
            data=data_in_table,
        )
        expected_table_object.id = "__input_" + id

        expected_table = dcc.Loading(
            html.Div(
                [
                    None,
                    html.Div(expected_table_object, id=id),
                ],
                className="table-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(custom_table, expected_table)

    def test_custom_dash_data_table_column_referral(self):
        """Tests whether a custom created table callable can be correctly built in vm.Table.

        This test focuses on the case that the custom grid include column referrals on presumed data knowledge.
        """
        id = "custom_dash_data_table"

        @capture("table")
        def custom_dash_data_table(data_frame):
            data_frame["cat"]  # access "existing" column
            return dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in data_frame.columns],
                data=data_frame.to_dict("records"),
            )

        table = vm.Table(
            id=id,
            figure=custom_dash_data_table(data_frame=data),
        )
        table.pre_build()

        custom_table = table.build()

        expected_table_object = dash_table.DataTable(
            columns=columns,
            data=data_in_table,
        )
        expected_table_object.id = "__input_" + id

        expected_table = dcc.Loading(
            html.Div(
                [
                    None,
                    html.Div(expected_table_object, id=id),
                ],
                className="table-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(custom_table, expected_table)
