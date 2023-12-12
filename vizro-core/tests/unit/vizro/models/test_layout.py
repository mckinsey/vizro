import numpy as np
import pytest
from pydantic import ValidationError

import vizro.models as vm
from vizro.models._layout import GAP_DEFAULT, MIN_DEFAULT, ColRowGridLines
from vizro.models._models_utils import get_unique_grid_component_ids


class TestLayoutInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_layout_mandatory_only(self):
        layout = vm.Layout(grid=[[0, 1], [0, 2]])
        assert hasattr(layout, "id")
        assert layout.grid == [[0, 1], [0, 2]]
        assert layout.col_gap == GAP_DEFAULT
        assert layout.row_gap == GAP_DEFAULT
        assert layout.col_min_width == MIN_DEFAULT
        assert layout.row_min_height == MIN_DEFAULT
        assert layout.component_grid_lines == [
            ColRowGridLines(col_start=1, col_end=2, row_start=1, row_end=3),
            ColRowGridLines(col_start=2, col_end=3, row_start=1, row_end=2),
            ColRowGridLines(col_start=2, col_end=3, row_start=2, row_end=3),
        ]

    @pytest.mark.parametrize("test_gap", ["0px", "4px", "8px"])
    def test_create_layout_mandatory_and_optional(self, test_gap):
        layout = vm.Layout(
            grid=[[0, 1], [0, 2]], col_gap=test_gap, row_gap=test_gap, col_min_width=test_gap, row_min_height=test_gap
        )

        assert hasattr(layout, "id")
        assert layout.grid == [[0, 1], [0, 2]]
        assert layout.col_gap == test_gap
        assert layout.row_gap == test_gap
        assert layout.col_min_width == test_gap
        assert layout.row_min_height == test_gap
        assert layout.component_grid_lines == [
            ColRowGridLines(col_start=1, col_end=2, row_start=1, row_end=3),
            ColRowGridLines(col_start=2, col_end=3, row_start=1, row_end=2),
            ColRowGridLines(col_start=2, col_end=3, row_start=2, row_end=3),
        ]

    def test_mandatory_grid_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Layout()


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
        with pytest.raises(ValidationError, match="value is not a valid list"):
            vm.Layout(grid=grid)

    @pytest.mark.parametrize(
        "grid",
        [
            [["Table Graph"], ["Table ."]],
            [["A"], ["B"], ["C"]],
        ],
    )
    def test_invalid_input_value(self, grid):
        with pytest.raises(ValidationError, match="value is not a valid integer"):
            vm.Layout(grid=grid)

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
            vm.Layout(grid=grid)

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
            vm.Layout(grid=grid)

    @pytest.mark.parametrize(
        "grid",
        [
            [[0, 1, 2], [3, 4]],
            [[0, 1], [2, 3, 4]],
        ],
    )
    def test_invalid_list_length(self, grid):
        with pytest.raises(ValidationError, match="All rows must be of same length."):
            vm.Layout(grid=grid)


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
            vm.Layout(grid=grid)
        except ValidationError as ve:
            assert False, f"{grid} raised a value error {ve}."


@pytest.mark.parametrize("grid", [[[0, -1], [1, 2]], [[0, -1, 1, 2]], [[-1, -1, -1], [0, 1, 2]]])
def test_get_unique_grid_component_ids(grid):
    result = get_unique_grid_component_ids(grid)
    expected = np.array([0, 1, 2])

    assert isinstance(result, np.ndarray)
    assert (result == expected).all()
