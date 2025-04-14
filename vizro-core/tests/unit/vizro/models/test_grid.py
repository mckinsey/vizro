import numpy as np
import pytest
from asserts import assert_component_equal
from dash import html
from pydantic import ValidationError

import vizro.models as vm
from vizro.models._grid import GAP_DEFAULT, MIN_DEFAULT, ColRowGridLines, _get_unique_grid_component_ids


class TestGridInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_grid_mandatory_only(self):
        grid = vm.Grid(grid=[[0, 1], [0, 2]])
        assert hasattr(grid, "id")
        assert grid.grid == [[0, 1], [0, 2]]
        assert grid.col_gap == GAP_DEFAULT
        assert grid.row_gap == GAP_DEFAULT
        assert grid.col_min_width == MIN_DEFAULT
        assert grid.row_min_height == MIN_DEFAULT
        assert grid.component_grid_lines == [
            ColRowGridLines(col_start=1, col_end=2, row_start=1, row_end=3),
            ColRowGridLines(col_start=2, col_end=3, row_start=1, row_end=2),
            ColRowGridLines(col_start=2, col_end=3, row_start=2, row_end=3),
        ]

    @pytest.mark.parametrize("test_unit", ["0px", "4px", "4rem", "4em", "4%"])
    def test_create_grid_mandatory_and_optional(self, test_unit):
        grid = vm.Grid(
            grid=[[0, 1], [0, 2]],
            col_gap=test_unit,
            row_gap=test_unit,
            col_min_width=test_unit,
            row_min_height=test_unit,
        )

        assert hasattr(grid, "id")
        assert grid.grid == [[0, 1], [0, 2]]
        assert grid.col_gap == test_unit
        assert grid.row_gap == test_unit
        assert grid.col_min_width == test_unit
        assert grid.row_min_height == test_unit
        assert grid.component_grid_lines == [
            ColRowGridLines(col_start=1, col_end=2, row_start=1, row_end=3),
            ColRowGridLines(col_start=2, col_end=3, row_start=1, row_end=2),
            ColRowGridLines(col_start=2, col_end=3, row_start=2, row_end=3),
        ]

    @pytest.mark.parametrize("test_unit", ["0", "calc(100% - 3px)", "4ex", "4ch", "4vh", "4vw", "4vmin", "4vmax"])
    def test_invalid_unit_size(self, test_unit):
        with pytest.raises(ValidationError, match="4 validation errors for Grid"):
            vm.Grid(
                grid=[[0, 1], [0, 2]],
                col_gap=test_unit,
                row_gap=test_unit,
                col_min_width=test_unit,
                row_min_height=test_unit,
            )

    def test_mandatory_grid_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Grid()


class TestMalformedGrid:
    """Tests validators to detect malformed grid."""

    @pytest.mark.parametrize(
        "grid",
        [
            0,
            [0],
            [-1],
            [[0], 1],
            [0, 1, 0],
            [0, 1, 3],
        ],
    )
    def test_invalid_input_type(self, grid):
        with pytest.raises(ValidationError, match="Input should be a valid list"):
            vm.Grid(grid=grid)

    @pytest.mark.parametrize(
        "grid",
        [
            [["Table Graph"], ["Table ."]],
            [["A"], ["B"], ["C"]],
        ],
    )
    def test_invalid_input_value(self, grid):
        with pytest.raises(ValidationError, match="Input should be a valid integer"):
            vm.Grid(grid=grid)

    @pytest.mark.parametrize(
        "grid",
        [
            [[0], [1], [0]],
            [[0, 1], [2, 0]],
            [[2, 0], [0, 1]],
            [[0, 1], [0, 0]],
            [[0, 0], [1, 0]],
            [[-1, 0], [0, -1]],
            [[-1, 0, 1], [0, -1, 1]],
            [[-1, 0, 1], [1, -1, 1]],
        ],
    )
    def test_invalid_grid_area(self, grid):
        with pytest.raises(ValidationError, match="Grid areas must be rectangular and not overlap!"):
            vm.Grid(grid=grid)

    @pytest.mark.parametrize(
        "grid",
        [
            [[1, 2], [3, 4]],
            [[0, 2], [3, 4]],
            [[6, 4], [2, 5]],
        ],
    )
    def test_invalid_int_sequence(self, grid):
        with pytest.raises(ValidationError, match="Grid must contain consecutive integers starting from 0."):
            vm.Grid(grid=grid)

    @pytest.mark.parametrize(
        "grid",
        [
            [[0, 1, 2], [3, 4]],
            [[0, 1], [2, 3, 4]],
        ],
    )
    def test_invalid_list_length(self, grid):
        with pytest.raises(ValidationError, match="All rows must be of same length."):
            vm.Grid(grid=grid)


class TestWorkingGrid:
    """Checks if working grid pass all validations."""

    @pytest.mark.parametrize(
        "grid",
        [
            [[0]],
            [[0], [1]],
            [[0, 1, 2]],
            [[0.0, 1.0, 2.0]],
            [[0, 1], [0, 2]],
            [[1, 0], [1, 0]],
            [[0, 0], [0, 0]],
            [[0, 1, 2], [3, 3, 3]],
            [[i] for i in range(10)],
            [[-1, 0], [1, 0]],
            [[-1, 0], [1, -1]],
            [[-1, -1, -1, -1], [0, 1, 2, 3]],
        ],
    )
    def test_working_grid(self, grid):
        try:
            vm.Grid(grid=grid)
        except ValidationError as ve:
            assert False, f"{grid} raised a value error {ve}."


class TestSharedGridHelpers:
    @pytest.mark.parametrize(
        "grid",
        [
            [[0, -1], [1, 2]],
            [[0, -1, 1, 2]],
            [[-1, -1, -1], [0, 1, 2]],
        ],
    )
    def test_get_unique_grid_component_ids(self, grid):
        result = _get_unique_grid_component_ids(grid)
        expected = np.array([0, 1, 2])

        np.testing.assert_array_equal(result, expected)

    def test_set_grid_valid(self, model_with_layout):
        model_with_layout(title="Title", components=[vm.Button(), vm.Button()], layout=vm.Grid(grid=[[0, 1]]))

    def test_set_grid_invalid(self, model_with_layout):
        with pytest.raises(ValidationError, match="Number of page and grid components need to be the same."):
            model_with_layout(title="Title", components=[vm.Button()], layout=vm.Grid(grid=[[0, 1]]))


class TestGridBuild:
    def test_grid_build(self):
        result = vm.Grid(id="grid_id", grid=[[0, 1], [0, 2]]).build()
        expected = html.Div(
            id="grid_id",
            children=[
                html.Div(
                    id="grid_id_0",
                    style={"gridColumn": "1/2", "gridRow": "1/3", "height": "100%", "width": "100%"},
                    className="grid-item",
                ),
                html.Div(
                    id="grid_id_1",
                    style={"gridColumn": "2/3", "gridRow": "1/2", "height": "100%", "width": "100%"},
                    className="grid-item",
                ),
                html.Div(
                    id="grid_id_2",
                    style={"gridColumn": "2/3", "gridRow": "2/3", "height": "100%", "width": "100%"},
                    className="grid-item",
                ),
            ],
            style={
                "gridRowGap": "24px",
                "gridColumnGap": "24px",
                "gridTemplateColumns": f"repeat(2,minmax({'0px'}, 1fr))",
                "gridTemplateRows": f"repeat(2,minmax({'0px'}, 1fr))",
            },
            className="grid-layout",
        )
        assert_component_equal(result, expected)
