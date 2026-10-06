"""Deprecated `AgGrid` model. Use [`Table`][vizro.models.Table] with a `dash_ag_grid` figure instead."""

# TODO[1.0.0]: delete this entire file. Also remove the `AgGrid` import + `__all__` entry in
#  `models/_components/__init__.py` and `models/__init__.py`. The re-exports below (Table/Trigger/CellClicked/
#  SelectedRow/CELL_CLICKED_MAPPING/DAG_AG_GRID_PROPERTIES) have no in-repo importers (they import from `table.py`)
#  so nothing internal breaks; keep them only if external back-compat for `from ...ag_grid_legacy import X` is wanted.

from typing import Annotated, Literal

from pydantic import AfterValidator, Field
from pydantic.json_schema import SkipJsonSchema
from typing_extensions import deprecated

from vizro.models._components._components_utils import _process_callable_data_frame

# The canonical implementation now lives in table.py. These are re-exported for backwards compatibility with any code
# importing them from `vizro.models._components.ag_grid_legacy`.
from vizro.models._components.table import (  # noqa: F401
    CELL_CLICKED_MAPPING,
    DAG_AG_GRID_PROPERTIES,
    CellClicked,
    SelectedRow,
    Table,
    Trigger,
)
from vizro.models.types import CapturedCallable


@deprecated(
    "`AgGrid` is deprecated and will not exist in Vizro 1.0.0 "
    "(https://vizro.readthedocs.io/en/stable/pages/API-reference/deprecations/#aggrid-model). "
    "Use `Table` with a `dash_ag_grid` figure instead: `vm.Table(figure=dash_ag_grid(...))`.",
    category=FutureWarning,
)
class AgGrid(Table):
    """Deprecated wrapper for `dash_ag_grid.AgGrid`.

    Deprecated: use [`Table`][vizro.models.Table] with a `dash_ag_grid` figure
    (`vm.Table(figure=dash_ag_grid(...))`), which is functionally identical.

    Abstract: Usage documentation
        [How to use an AgGrid](../user-guides/table.md#ag-grid)

    """

    # Keep `type="ag_grid"` so existing YAML/JSON `type: ag_grid` configs still route to this (deprecated) model.
    type: Literal["ag_grid"] = "ag_grid"  # type: ignore[assignment]
    # Restrict `AgGrid` to an AG Grid figure. (`Table` itself also accepts the deprecated Dash DataTable figure.)
    figure: Annotated[
        SkipJsonSchema[CapturedCallable],
        AfterValidator(_process_callable_data_frame),
        Field(
            json_schema_extra={"mode": "ag_grid", "import_path": "vizro.tables"},
            description="Function that returns a `Dash AG Grid`.",
        ),
    ]

    @property
    def _is_ag_grid(self) -> bool:
        # `AgGrid` locks `figure` to ag_grid mode (see the field override above), so it is always an AG Grid - even
        # when the figure is an unresolved CapturedCallable whose `_mode` is None (e.g. when
        # `allow_undefined_captured_callable` is used). This overrides `Table._is_ag_grid`, which infers the backing
        # from `figure._mode` and would otherwise misclassify such an `AgGrid` as a Dash DataTable.
        return True
