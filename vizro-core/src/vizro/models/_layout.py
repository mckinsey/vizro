from typing import List, NamedTuple, Optional, Tuple

import numpy as np
from numpy import ma
from pydantic import Field, PrivateAttr, ValidationError, validator

from vizro._constants import EMPTY_SPACE_CONST
from vizro.models import VizroBaseModel
from vizro.models._models_utils import get_unique_grid_component_ids

GAP_DEFAULT = "12px"
MIN_DEFAULT = "0px"


class ColRowGridLines(NamedTuple):
    """Stores CSS grid lines of grid area spanned by component."""

    col_start: int
    col_end: int
    row_start: int
    row_end: int


def _convert_to_combined_grid_coord(matrix: ma.MaskedArray) -> ColRowGridLines:
    """Converts matrix coordinates from user `grid` to one combined grid area spanned by component i.

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


def _convert_to_single_grid_coord(matrix: ma.MaskedArray) -> List[ColRowGridLines]:
    """Converts matrix coordinates from user `grid` to list of grid areas spanned by each placement of component i.

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
    """Checks if rectangles r1 and r2 overlap in areas.

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


def _validate_grid_areas(grid_areas: List[ColRowGridLines]) -> None:
    """Validates grid areas spanned by screen components in `Layout`."""
    for i, r1 in enumerate(grid_areas):
        for r2 in grid_areas[i + 1 :]:
            if _do_rectangles_overlap(r1, r2):
                raise ValueError("Grid areas must be rectangular and not overlap!")


def _get_grid_lines(grid: List[List[int]]) -> Tuple[List[ColRowGridLines], List[ColRowGridLines]]:
    """Gets list of ColRowGridLines for components and spaces on screen for validation and placement."""
    component_grid_lines = []
    unique_grid_idx = get_unique_grid_component_ids(grid)
    for component_idx in unique_grid_idx:
        matrix = ma.masked_equal(grid, component_idx)
        component_grid_lines.append(_convert_to_combined_grid_coord(matrix))

    matrix = ma.masked_equal(grid, EMPTY_SPACE_CONST)
    space_grid_lines = _convert_to_single_grid_coord(matrix=matrix)

    return component_grid_lines, space_grid_lines


class Layout(VizroBaseModel):
    """Grid specification to place chart/components on the [`Page`][vizro.models.Page].

    Args:
        grid (List[List[int]]): Grid specification to arrange components on screen.
        row_gap (str): Gap between rows in px. Defaults to `"12px"`.
        col_gap (str): Gap between columns in px. Defaults to `"12px"`.
        row_min_height (str): Minimum row height in px. Defaults to `"0px"`.
        col_min_width (str): Minimum column width in px. Defaults to `"0px"`.
    """

    grid: List[List[int]] = Field(..., description="Grid specification to arrange components on screen.")
    row_gap: str = Field(GAP_DEFAULT, description="Gap between rows in px. Defaults to 12px.", regex="[0-9]+px")
    col_gap: str = Field(GAP_DEFAULT, description="Gap between columns in px. Defaults to 12px.", regex="[0-9]+px")
    row_min_height: str = Field(MIN_DEFAULT, description="Minimum row height in px. Defaults to 0px.", regex="[0-9]+px")
    col_min_width: str = Field(
        MIN_DEFAULT, description="Minimum column width in px. Defaults to 0px.", regex="[0-9]+px"
    )
    _component_grid_lines: Optional[List[ColRowGridLines]] = PrivateAttr()

    @validator("grid")
    def validate_grid(cls, grid):
        if len({len(row) for row in grid}) > 1:
            raise ValueError("All rows must be of same length.")

        # Validate grid type and values
        unique_grid_idx = get_unique_grid_component_ids(grid)
        if 0 not in unique_grid_idx or not np.array_equal(unique_grid_idx, np.arange((unique_grid_idx.max() + 1))):
            raise ValueError("Grid must contain consecutive integers starting from 0.")

        # Validates grid areas spanned by components and spaces
        component_grid_lines, space_grid_lines = _get_grid_lines(grid)
        _validate_grid_areas(component_grid_lines + space_grid_lines)
        return grid

    def __init__(self, **data):
        super().__init__(**data)
        self._component_grid_lines = _get_grid_lines(self.grid)[0]

    @property
    def component_grid_lines(self):
        return self._component_grid_lines


if __name__ == "__main__":
    print(repr(Layout(grid=[[0, 1], [0, 2]])))  # noqa: T201

    try:
        Layout(grid=[[0, 1], [1, 0]])
    except ValidationError as e:
        print(e)  # noqa: T201
