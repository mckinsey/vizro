import pandas as pd
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
        assert table.columns == [
            {"id": "cat", "name": "cat"},
            {"id": "int", "name": "int"},
            {"id": "float", "name": "float"},
            {"id": "date", "name": "date"},
        ]
        assert table.data == [
            {"cat": "a", "date": pd.Timestamp("2021-01-01 00:00:00"), "float": 7.3, "int": 4},
            {"cat": "b", "date": pd.Timestamp("2021-01-02 00:00:00"), "float": 8.2, "int": 5},
            {"cat": "c", "date": pd.Timestamp("2021-01-03 00:00:00"), "float": 9.1, "int": 6},
        ]
        # we could test other properties such as style_header,
        # but this would just test our chosen defaults, and no functionality really
