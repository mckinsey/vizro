import dash_ag_grid as dag
import pandas as pd
import vizro.models as vm
from asserts import assert_component_equal
from dash import dcc, html
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
                    dag.AgGrid(id="__input_custom_ag_grid", columnDefs=[], rowData=[]),
                    id=id,
                    className="table-container",
                ),
            ],
            id=f"{id}_outer",
            color="grey",
            parent_className="loading-container",
        )

        assert_component_equal(custom_grid, expected_grid)
