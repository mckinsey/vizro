import numpy as np
import pytest
from asserts import assert_component_equal
from dash import html
from pydantic import TypeAdapter, ValidationError

import vizro.models as vm
from vizro.models._grid import GAP_DEFAULT, MIN_DEFAULT, ColRowGridLines, _get_unique_grid_component_ids
from vizro.models.types import LayoutType

pytestmark = [
    pytest.mark.filterwarnings("ignore:The `Layout` model has been renamed `Grid`:FutureWarning"),
    pytest.mark.filterwarnings("ignore:`layout` without an explicit `type`:FutureWarning"),
]


class TestLayoutInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_layout_deprecated(self):
        with pytest.warns(FutureWarning, match="The `Layout` model has been renamed `Grid`"):
            vm.Layout(grid=[[0]])

    def test_layout_deprecated_yaml(self):
        # Test dictionary configuration of a layout without discriminator "type" specified. To do this outside the
        # context of a Page/Container model we need to use TypeAdapter. The behavior here should be equivalent to
        # specifying vm.Layout but with an extra warning.
        # Resolve ForwardRefs for TypeAdapter:
        Grid = vm.Grid  # noqa: F841
        Flex = vm.Flex  # noqa: F841
        Layout = vm.Layout  # noqa: F841

        with (
            pytest.warns(FutureWarning, match="The `Layout` model has been renamed `Grid`"),
            pytest.warns(FutureWarning, match="`layout` without an explicit `type`"),
        ):
            layout = TypeAdapter(LayoutType).validate_python({"grid": [[0]]})

        # Use type rather than isinstance to not pass if it's a subclass.
        assert type(layout) is vm.Layout

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

    @pytest.mark.parametrize("test_unit", ["0px", "4px", "4rem", "4em", "4%"])
    def test_create_layout_mandatory_and_optional(self, test_unit):
        layout = vm.Layout(
            grid=[[0, 1], [0, 2]],
            col_gap=test_unit,
            row_gap=test_unit,
            col_min_width=test_unit,
            row_min_height=test_unit,
        )

        assert hasattr(layout, "id")
        assert layout.grid == [[0, 1], [0, 2]]
        assert layout.col_gap == test_unit
        assert layout.row_gap == test_unit
        assert layout.col_min_width == test_unit
        assert layout.row_min_height == test_unit
        assert layout.component_grid_lines == [
            ColRowGridLines(col_start=1, col_end=2, row_start=1, row_end=3),
            ColRowGridLines(col_start=2, col_end=3, row_start=1, row_end=2),
            ColRowGridLines(col_start=2, col_end=3, row_start=2, row_end=3),
        ]

    @pytest.mark.parametrize("test_unit", ["0", "calc(100% - 3px)", "4ex", "4ch", "4vh", "4vw", "4vmin", "4vmax"])
    def test_invalid_unit_size(self, test_unit):
        with pytest.raises(ValidationError, match="4 validation errors for Layout"):
            vm.Layout(
                grid=[[0, 1], [0, 2]],
                col_gap=test_unit,
                row_gap=test_unit,
                col_min_width=test_unit,
                row_min_height=test_unit,
            )

    def test_mandatory_grid_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
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
        with pytest.raises(ValidationError, match="Input should be a valid list"):
            vm.Layout(grid=grid)

    @pytest.mark.parametrize(
        "grid",
        [
            [["Table Graph"], ["Table ."]],
            [["A"], ["B"], ["C"]],
        ],
    )
    def test_invalid_input_value(self, grid):
        with pytest.raises(ValidationError, match="Input should be a valid integer"):
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


class TestSharedLayoutHelpers:
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

    def test_set_layout_valid(self, model_with_layout):
        model_with_layout(title="Title", components=[vm.Button(), vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    def test_set_layout_invalid(self, model_with_layout):
        with pytest.raises(ValidationError, match="Number of page and grid components need to be the same."):
            model_with_layout(title="Title", components=[vm.Button()], layout=vm.Layout(grid=[[0, 1]]))


class TestLayoutBuild:
    def test_layout_build(self):
        result = vm.Layout(id="layout_id", grid=[[0, 1], [0, 2]]).build()
        expected = html.Div(
            id="layout_id",
            children=[
                html.Div(
                    id="layout_id_0",
                    style={"gridColumn": "1/2", "gridRow": "1/3", "height": "100%", "width": "100%"},
                    className="grid-item",
                ),
                html.Div(
                    id="layout_id_1",
                    style={"gridColumn": "2/3", "gridRow": "1/2", "height": "100%", "width": "100%"},
                    className="grid-item",
                ),
                html.Div(
                    id="layout_id_2",
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
