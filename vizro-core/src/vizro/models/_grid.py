import re
from typing import Annotated, Any, Literal, NamedTuple, Optional

import numpy as np
from dash import html
from numpy import ma
from pydantic import AfterValidator, Field, PrivateAttr, ValidationInfo
from typing_extensions import deprecated

from vizro._constants import EMPTY_SPACE_CONST, GAP_DEFAULT
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

MIN_DEFAULT = "0px"


class ColRowGridLines(NamedTuple):
    """Stores CSS grid lines of grid area spanned by component."""

    col_start: int
    col_end: int
    row_start: int
    row_end: int


def _get_unique_grid_component_ids(grid: list[list[int]]):
    unique_grid_idx = np.unique(grid)
    unique_grid_comp_idx = unique_grid_idx[unique_grid_idx != EMPTY_SPACE_CONST]
    return unique_grid_comp_idx


# Validators for reuse
def set_layout(layout, info: ValidationInfo):
    from vizro.models import Flex, Grid

    # No validation for Flex layout
    # Possibly some of this validator should be attached directly to the Grid model type rather than
    # the LayoutType Union to avoid needing this check.
    if isinstance(layout, Flex):
        return layout

    # This exists only to eagerly raise the error, otherwise obscure error message on eg Page()
    # Same for similar code in other places
    # TODO[MS]: find another solution that clashes less with typing
    if "components" not in info.data:
        return layout

    if layout is None:
        grid = [[i] for i in range(len(info.data["components"]))]
        return Grid(grid=grid)

    unique_grid_idx = _get_unique_grid_component_ids(layout.grid)
    if len(unique_grid_idx) != len(info.data["components"]):
        raise ValueError("Number of page and grid components need to be the same.")
    return layout


def validate_grid(grid):
    if len({len(row) for row in grid}) > 1:
        raise ValueError("All rows must be of same length.")

    # Validate grid type and values
    unique_grid_idx = _get_unique_grid_component_ids(grid)
    if 0 not in unique_grid_idx or not np.array_equal(unique_grid_idx, np.arange(unique_grid_idx.max() + 1)):
        raise ValueError("Grid must contain consecutive integers starting from 0.")

    # Validates grid areas spanned by components and spaces
    component_grid_lines, space_grid_lines = _get_grid_lines(grid)
    _validate_grid_areas(component_grid_lines + space_grid_lines)
    return grid


def _convert_to_combined_grid_coord(matrix: ma.MaskedArray) -> ColRowGridLines:
    """Converts `matrix` coordinates from user `grid` to one combined grid area spanned by component i.

    Required for validation of grid areas spanned by components.

    User-provided grid:  [[0, 1], [0, 2]]
    Matrix coordinates for component i=0: [(0, 0), (1, 0)]
    Grid coordinates for component i=0: ColRowGridLines(col_start=1, col_end=2, row_start=1, row_end=3)

    Args:
        matrix: Array that represents the user-provided grid with a mask on the relevant screen component i

    Returns:
        ColRowGridLines for combined area spanned by all placements of screen component i

    """
    matrix_coord = [(x, y) for x, row in enumerate(matrix) for y, value in enumerate(row) if ma.is_masked(value)]

    row_idx, col_idx = zip(*matrix_coord)
    return ColRowGridLines(
        col_start=min(col_idx) + 1, col_end=max(col_idx) + 2, row_start=min(row_idx) + 1, row_end=max(row_idx) + 2
    )


def _convert_to_single_grid_coord(matrix: ma.MaskedArray) -> list[ColRowGridLines]:
    """Converts `matrix` coordinates from user `grid` to list of grid areas spanned by each placement of component i.

    Required for validation of grid areas spanned by spaces, where the combined area does not need to be rectangular.

    User-provided grid:  [[0, 1], [0, 2]]
    Matrix coordinates for component i=0: [(0, 0), (1, 0)]
    Grid coordinates for component i=0: [ColRowGridLines(col_start=1, col_end=2, row_start=1, row_end=2),
                                         ColRowGridLines(col_start=1, col_end=2, row_start=2, row_end=3)]

    Args:
        matrix: Array that represents the user-provided grid with a mask on the relevant screen component i

    Returns:
        List of ColRowGridLines for each individual placement of screen component i

    """
    matrix_coord = [(x, y) for x, row in enumerate(matrix) for y, value in enumerate(row) if ma.is_masked(value)]

    return [
        ColRowGridLines(col_start=col_idx + 1, col_end=col_idx + 2, row_start=row_idx + 1, row_end=row_idx + 2)
        for row_idx, col_idx in matrix_coord
    ]


def _do_rectangles_overlap(r1: ColRowGridLines, r2: ColRowGridLines) -> bool:
    """Checks if rectangles `r1` and `r2` overlap in areas.

    1. Computes the min and max of r1 and r2 on both axes.
    2. Computes the boundaries of the intersection rectangle (x1=left, x2=right, y1=top, y2=bottom)
    3. Checks if the intersection is valid and has a positive non-zero area (x1 < x2 and y1 < y2)

    See: https://github.com/SFML/SFML/blob/12d81304e63e333174d943ba3ff572e38abd56e0/include/SFML/Graphics/Rect.inl#L109

    Args:
        r1: Tuple containing grid coordinates for screen component i
        r2: Tuple containing grid coordinates for screen component j

    Returns:
        Bool if rectangular grid area spanned by component i overlaps with the area of component j

    """
    x1 = max(min(r1.row_start, r1.row_end), min(r2.row_start, r2.row_end))
    y1 = max(min(r1.col_start, r1.col_end), min(r2.col_start, r2.col_end))
    x2 = min(max(r1.row_start, r1.row_end), max(r2.row_start, r2.row_end))
    y2 = min(max(r1.col_start, r1.col_end), max(r2.col_start, r2.col_end))
    return x1 < x2 and y1 < y2


def _validate_grid_areas(grid_areas: list[ColRowGridLines]) -> None:
    """Validates `grid_areas` spanned by screen components in `Grid`."""
    for i, r1 in enumerate(grid_areas):
        for r2 in grid_areas[i + 1 :]:
            if _do_rectangles_overlap(r1, r2):
                raise ValueError("Grid areas must be rectangular and not overlap!")


def _get_grid_lines(grid: list[list[int]]) -> tuple[list[ColRowGridLines], list[ColRowGridLines]]:
    """Gets list of ColRowGridLines for components and spaces on screen for validation and placement."""
    component_grid_lines = []
    unique_grid_idx = _get_unique_grid_component_ids(grid)
    for component_idx in unique_grid_idx:
        matrix = ma.masked_equal(grid, component_idx)
        component_grid_lines.append(_convert_to_combined_grid_coord(matrix))

    matrix = ma.masked_equal(grid, EMPTY_SPACE_CONST)
    space_grid_lines = _convert_to_single_grid_coord(matrix=matrix)

    return component_grid_lines, space_grid_lines


class Grid(VizroBaseModel):
    """Grid specification to place chart/components on the [`Page`][vizro.models.Page].

    Args:
        type (Literal["grid"]): Defaults to `"grid"`.
        grid (list[list[int]]): Grid specification to arrange components on screen.
        row_gap (str): Specifies the gap between rows. Allowed units: 'px', 'rem', 'em', or '%'. Defaults to `24px`.
        col_gap (str): Specifies the gap between columns. Allowed units: 'px', 'rem', 'em', or '%'. Defaults to `24px`.
        row_min_height (str): Minimum row height in px. Allowed units: 'px', 'rem', 'em', or '%'. Defaults to `0px`.
        col_min_width (str): Minimum column width in px. Allowed unit are: 'px', 'rem', 'em', or '%'. Defaults to `0px`.

    """

    type: Literal["grid"] = "grid"
    grid: Annotated[
        list[list[int]],
        AfterValidator(validate_grid),
        Field(description="Grid specification to arrange components on screen."),
    ]
    row_gap: str = Field(
        default=GAP_DEFAULT,
        description="Specifies the gap between rows. Allowed units: 'px', 'rem', 'em', or '%'. Defaults to `24px`.",
        pattern=re.compile(r"^\d+(px|rem|em|%)$"),
    )
    col_gap: str = Field(
        default=GAP_DEFAULT,
        description="Specifies the gap between columns. Allowed units: 'px', 'rem', 'em', or '%'. Defaults to `24px`.",
        pattern=re.compile(r"^\d+(px|rem|em|%)$"),
    )
    row_min_height: str = Field(
        default=MIN_DEFAULT,
        description="Minimum row height in px. Allowed units: 'px', 'rem', 'em', or '%'. Defaults to `0px`.",
        pattern=re.compile(r"^\d+(px|rem|em|%)$"),
    )
    col_min_width: str = Field(
        default=MIN_DEFAULT,
        description="Minimum column width in px. Allowed units: 'px', 'rem', 'em', or '%'. Defaults to `0px`.",
        pattern=re.compile(r"^\d+(px|rem|em|%)$"),
    )
    _component_grid_lines: Optional[list[ColRowGridLines]] = PrivateAttr()

    def model_post_init(self, context: Any) -> None:
        self._component_grid_lines = _get_grid_lines(self.grid)[0]

    @property
    def component_grid_lines(self):
        return self._component_grid_lines

    # The return type has a contract in which each component has a key f"{layout.id}_{component_idx}".
    # We could have _LayoutBuildType as a return type annotation, but it would need to be generated
    # dynamically which is tricky and not amenable to type checking anyway.
    # Possibly in future we would have a public method to generate this string or maybe even
    # a new method Grid.inject or similar that handles the injection of components into the grid for us.
    # Another alternative is to take [component.build() for component in components] as an argument
    # in the build method here.
    @_log_call
    def build(self):
        """Creates empty container with inline style to later position components in."""
        components_content = [
            html.Div(
                id=f"{self.id}_{component_idx}",
                style={
                    "gridColumn": f"{grid_coord.col_start}/{grid_coord.col_end}",
                    "gridRow": f"{grid_coord.row_start}/{grid_coord.row_end}",
                    "height": "100%",
                    "width": "100%",
                },
                className="grid-item",
            )
            for component_idx, grid_coord in enumerate(self.component_grid_lines)
        ]

        component_container = html.Div(
            components_content,
            style={
                "gridRowGap": self.row_gap,
                "gridColumnGap": self.col_gap,
                "gridTemplateColumns": f"repeat({len(self.grid[0])},minmax({self.col_min_width}, 1fr))",
                "gridTemplateRows": f"repeat({len(self.grid)},minmax({self.row_min_height}, 1fr))",
            },
            className="grid-layout",
            id=self.id,
        )
        return component_container


@deprecated(
    "The `Layout` model has been renamed `Grid`, and `Layout` will no longer exist in Vizro 0.2.0. To ensure future "
    "compatibility, replace your references to `vm.Layout` with `vm.Grid`.",
    category=FutureWarning,
)
class Layout(Grid):
    """Deprecated. This model has been renamed [`Grid`][vizro.models.Grid]."""

    type: Literal["legacy_layout"] = "legacy_layout"  # type: ignore[assignment]
