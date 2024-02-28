import pandas as pd
from asserts import assert_component_equal
from dash import dash_table
from vizro.tables import dash_data_table

data = pd.DataFrame(
    {
        "cat": ["a", "b", "c"],
        "int": [4, 5, 6],
        "float": [7.3, 8.2, 9.1],
        "date": pd.to_datetime(["2021/01/01", "2021/01/02", "2021/01/03"]),
    }
)


class TestDashDataTable:
    def test_dash_data_table(self):
        table = dash_data_table(data_frame=data)()
        assert_component_equal(
            table,
            dash_table.DataTable(
                columns=[
                    {"id": "cat", "name": "cat"},
                    {"id": "int", "name": "int"},
                    {"id": "float", "name": "float"},
                    {"id": "date", "name": "date"},
                ],
                data=[
                    {"cat": "a", "int": 4, "float": 7.3, "date": pd.Timestamp("2021-01-01 00:00:00")},
                    {"cat": "b", "int": 5, "float": 8.2, "date": pd.Timestamp("2021-01-02 00:00:00")},
                    {"cat": "c", "int": 6, "float": 9.1, "date": pd.Timestamp("2021-01-03 00:00:00")},
                ],
            ),
            keys_to_strip={"style_as_list_view", "style_data", "style_header"},
        )

        # we could test other properties such as style_header,
        # but this would just test our chosen defaults, and no functionality really
