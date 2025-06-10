import dash_ag_grid as dag
import pandas as pd
from asserts import assert_component_equal
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
    "flex": 1,
}


class TestDashAgGrid:
    def test_dash_ag_grid(self):
        grid = dash_ag_grid(data_frame=data)()
        assert_component_equal(
            grid,
            dag.AgGrid(
                columnDefs=column_defs,
                rowData=row_data_date_converted,
                defaultColDef=default_col_defs,
            ),
            keys_to_strip={"className", "dashGridOptions"},
        )
        # skipping only dashGridOptions as this is mostly our defaults for data formats, and would crowd the tests

    def test_custom_dash_ag_grid(self):
        @capture("ag_grid")
        def custom_dash_ag_grid(data_frame):
            return dag.AgGrid(
                columnDefs=[{"field": col} for col in data_frame.columns],
                rowData=data_frame.to_dict("records"),
            )

        ag_grid = custom_dash_ag_grid(data_frame=data)()

        assert_component_equal(
            ag_grid,
            dag.AgGrid(
                rowData=row_data_date_raw,
                columnDefs=column_defs,
            ),
        )
