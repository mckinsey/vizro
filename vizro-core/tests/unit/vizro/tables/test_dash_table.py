import pandas as pd
from asserts import assert_component_equal
from dash import dash_table

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
                style_data={"border_bottom": "1px solid var(--border-subtleAlpha01)", "height": "40px"},
                style_header={
                    "border_bottom": "1px solid var(--stateOverlays-selectedHover)",
                    "border_top": "None",
                    "height": "32px",
                },
                style_data_conditional=[
                    {
                        "if": {"state": "active"},
                        "backgroundColor": "var(--stateOverlays-selected)",
                        "border": "1px solid var(--stateOverlays-selected)",
                    }
                ],
            ),
        )

    def test_custom_dash_data_table(self):
        @capture("table")
        def custom_dash_data_table(data_frame):
            return dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in data_frame.columns],
                data=data_frame.to_dict("records"),
            )

        table = custom_dash_data_table(data_frame=data)()

        assert_component_equal(
            table,
            dash_table.DataTable(
                data=data_in_table,
                columns=columns,
            ),
        )
