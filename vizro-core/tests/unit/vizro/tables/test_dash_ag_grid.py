import dash_ag_grid as dag
import pandas as pd
from asserts import assert_component_equal
from vizro.tables import dash_ag_grid

data = pd.DataFrame(
    {
        "cat": ["a", "b", "c"],
        "int": [4, 5, 6],
        "float": [7.3, 8.2, 9.1],
        "date": pd.to_datetime(["2021/01/01", "2021/01/02", "2021/01/03"]),
    }
)


class TestDashAgGrid:
    def test_dash_ag_grid(self):
        grid = dash_ag_grid(data_frame=data)()
        assert_component_equal(
            grid,
            dag.AgGrid(
                columnDefs=[{"field": "cat"}, {"field": "int"}, {"field": "float"}, {"field": "date"}],
                rowData=[
                    {"cat": "a", "int": 4, "float": 7.3, "date": "2021-01-01"},
                    {"cat": "b", "int": 5, "float": 8.2, "date": "2021-01-02"},
                    {"cat": "c", "int": 6, "float": 9.1, "date": "2021-01-03"},
                ],
            ),
            keys_to_strip={"className", "defaultColDef", "dashGridOptions", "style"},
        )
        # we could test other properties such as defaultColDef,
        # but this would just test our chosen defaults, and no functionality really
