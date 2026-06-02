"""Reference patterns for AG Grid tables in Vizro.

Source: https://vizro.readthedocs.io/en/stable/pages/user-guides/table/
        https://vizro.readthedocs.io/en/stable/pages/user-guides/custom-tables/

Vizro AG Grid = ``vm.AgGrid`` model + the ``dash_ag_grid`` factory from
``vizro.tables``. It wraps Dash AG Grid (https://dash.plotly.com/dash-ag-grid),
so treat those docs as authoritative for kwargs (``columnDefs``,
``defaultColDef``, ``dashGridOptions``, ``columnSize``, ``cellStyle``,
``rowData``, etc.). Colors come from ``vizro.themes.colors`` — never hardcode
hex.

Do NOT use:
  - ``vm.Table`` / Dash DataTable — AG Grid is the only table component.
  - Plotly-as-table (``px.imshow`` annotated, heatmap-with-text, etc.). The
    only lighter alternatives are KPI cards or a bar chart.
  - JS-only AG Grid features (event handlers like ``onCellClicked``, server-
    side row models, JS ``cellRenderer``s registered via the assets folder)
    — prefer ``cellStyle`` / ``valueFormatter`` config instead.

Two patterns:
  1. **Drop-in ``dash_ag_grid`` factory** — static config evaluated once at
     build time. Covers ~all real-world customization.
  2. **``@capture("ag_grid")`` custom function** — only when something must
     be recomputed at *render* time: a ``vm.Parameter`` drives the grid
     (Pattern 2 below), or ``columnDefs`` derive from the actual data shape
     (see ``writing-vizro-yaml/references/yaml-reference.md`` ``heatmap_grid``).

When you go custom, return a raw ``dash_ag_grid.AgGrid(...)`` and pass
``dashGridOptions={...}`` plus ``className="ag-theme-vizro"`` explicitly.
The built-in factory sets those up; a raw ``AgGrid`` doesn't, and
``vm.AgGrid.__call__`` runs ``figure.dashGridOptions.setdefault(...)`` on
every code path — without the kwarg the attribute doesn't exist and the
page-load callback crashes with
``AttributeError: 'AgGrid' object has no attribute 'dashGridOptions'``.
"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.themes import colors

df = px.data.gapminder()


# ---------------------------------------------------------------------------
# Pattern 1 — Drop-in ``dash_ag_grid`` factory
# ---------------------------------------------------------------------------

# Cell styling lives *inside* the relevant columnDef so it travels with the
# column. Colors picked from ``vizro.themes.colors`` to respect the theme.
column_defs = [
    {"field": "country"},
    {"field": "continent"},
    {"field": "year"},
    {"field": "lifeExp", "cellDataType": "numeric"},
    {"field": "pop", "cellDataType": "numeric"},
    {
        "field": "gdpPercap",
        "cellDataType": "dollar",  # "dollar" | "euro" | "percent" | "numeric"
        # World-Bank income brackets, rendered as a heatmap.
        "cellStyle": {
            "styleConditions": [
                {"condition": "params.value < 1045", "style": {"backgroundColor": colors.warning_500}},
                {
                    "condition": "params.value >= 1045 && params.value <= 4095",
                    "style": {"backgroundColor": colors.yellow_500},
                },
                {
                    "condition": "params.value > 4095 && params.value <= 12695",
                    "style": {"backgroundColor": colors.blue_500},
                },
                {"condition": "params.value > 12695", "style": {"backgroundColor": colors.green_500}},
            ]
        },
    },
]

drop_in_page = vm.Page(
    title="Sales table",
    components=[
        vm.AgGrid(
            id="sales_table",
            title="Country GDP detail",
            figure=dash_ag_grid(
                data_frame=df,
                columnDefs=column_defs,
                defaultColDef={"resizable": True, "filter": True, "sortable": True},
                dashGridOptions={"pagination": False},  # ON by default; disable for short tables.
                columnSize="responsiveSizeToFit",  # "autoSize" | "sizeToFit" | "responsiveSizeToFit" | None
            ),
        )
    ],
)


# ---------------------------------------------------------------------------
# Pattern 2 — Custom ``@capture("ag_grid")`` driven by a ``vm.Parameter``
# ---------------------------------------------------------------------------

from dash_ag_grid import AgGrid
from vizro.models.types import capture


@capture("ag_grid")
def column_picker_grid(chosen_columns: list[str], data_frame=None):
    """Show only the user-picked columns; Vizro re-runs this whenever the Dropdown below changes."""
    return AgGrid(
        className="ag-theme-vizro",
        columnDefs=[{"field": col} for col in chosen_columns],
        rowData=data_frame.to_dict("records"),
        dashGridOptions={"domLayout": "autoHeight", "pagination": True, "paginationPageSize": 20},
        defaultColDef={"resizable": True, "sortable": True, "filter": True, "flex": 1, "minWidth": 70},
    )


custom_page = vm.Page(
    title="Sales table — column picker",
    components=[
        vm.AgGrid(
            id="custom_ag_grid",
            title="Pick columns to display",
            figure=column_picker_grid(
                data_frame=df,
                chosen_columns=["country", "continent", "lifeExp", "pop", "gdpPercap"],
            ),
        )
    ],
    controls=[
        # ``<component_id>.<kwarg>`` — Vizro re-invokes ``column_picker_grid``
        # with the new list whenever this Dropdown changes.
        vm.Parameter(
            targets=["custom_ag_grid.chosen_columns"],
            selector=vm.Dropdown(
                title="Columns",
                options=["country", "continent", "year", "lifeExp", "pop", "gdpPercap"],
                value=["country", "continent", "lifeExp", "pop", "gdpPercap"],
                multi=True,
            ),
        ),
    ],
)


if __name__ == "__main__":
    Vizro().build(vm.Dashboard(pages=[drop_in_page, custom_page])).run()
