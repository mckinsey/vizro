"""Reference patterns for AG Grid tables in Vizro.

Source: https://vizro.readthedocs.io/en/stable/pages/user-guides/table/
        https://vizro.readthedocs.io/en/stable/pages/user-guides/custom-tables/

What this is
------------
Vizro AG Grid = ``vm.AgGrid`` model + the ``dash_ag_grid`` factory from
``vizro.tables``. Under the hood it wraps Dash AG Grid
(https://dash.plotly.com/dash-ag-grid), which itself wraps JS AG Grid.

What to ignore (do NOT use)
---------------------------
  - ``vm.Table`` / Dash DataTable. AG Grid is the only table component
    you should write — never reach for DataTable, even for small tables.
  - Plotly-as-table hacks: heatmap-with-text, scatter-with-text,
    ``px.imshow`` annotated as a table. Use AG Grid; the only acceptable
    lighter alternatives are KPI cards or a bar chart (see below).
  - JS-only AG Grid features: event-handler functions like
    ``onCellClicked``, server-side row models, JS ``cellRenderer``
    components registered via ``window.dashAgGridComponentFunctions``
    require an assets-folder ``.js`` file and rarely earn their keep —
    prefer ``cellStyle`` / ``valueFormatter`` config instead.

Knowledge mapping (Vizro vs Dash vs JS)
---------------------------------------
  - Dash AG Grid kwargs flow through to ``dash_ag_grid(...)``:
    ``columnDefs``, ``defaultColDef``, ``dashGridOptions``,
    ``columnSize``, ``cellStyle``, ``rowData``, ``getRowStyle``, etc.
    If the Dash AG Grid docs list it as a component prop, Vizro accepts
    it. Treat the Dash AG Grid docs as authoritative for the kwarg set.
  - JS-only AG Grid features (events, callbacks, server-side row model
    from ag-grid-community / ag-grid-enterprise JS docs) do NOT pass
    through. Ignore your prior knowledge of those.

When to choose AG Grid vs simpler alternatives
----------------------------------------------
  - Sortable / filterable / paginated detail tables with cell-level
    formatting or conditional styling → AG Grid.
  - 1-10 row scoreboards → KPI cards (no table needed).
  - "Top N" rankings → horizontal bar chart.

Two patterns for adding an AG Grid
----------------------------------
  1. Drop-in via the ``dash_ag_grid`` factory (preferred). Vizro
     handles config + theming automatically.
  2. Custom via ``@capture("ag_grid")`` when you need columnDefs
     derived from the data, or features the factory doesn't expose.

Both patterns wire the returned object into ``vm.AgGrid(figure=...)``.

Custom @capture("ag_grid") rules
--------------------------------
  - The decorated function MUST accept the DataFrame argument under the
    exact name ``data_frame`` (not ``df``, not ``data``). Vizro injects
    the DataFrame by that keyword.
  - The function can return either: (a) a raw
    ``dash_ag_grid.AgGrid(...)`` instance, as Pattern 2 below shows, or
    (b) a call to Vizro's ``dash_ag_grid(...)`` factory. If returning
    Vizro's factory inside a captured callable triggers a
    ``CapturedCallable`` serialization error, call
    ``dash_ag_grid.__wrapped__(data_frame=..., columnDefs=...)`` instead
    to bypass the wrapper.
"""

# ---------------------------------------------------------------------------
# Pattern 1 — Drop-in
# ---------------------------------------------------------------------------

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

df = px.data.gapminder()

# Column definitions are OPTIONAL — without them Vizro auto-infers
# columns from the DataFrame. Provide ``columnDefs`` only when you need
# cell-data-type formatting or column-level overrides.
column_defs = [
    {"field": "country"},
    {"field": "year"},
    {"field": "lifeExp", "cellDataType": "numeric"},
    {"field": "pop", "cellDataType": "numeric"},
    {"field": "gdpPercap", "cellDataType": "dollar"},
]
# Valid cellDataType values: "dollar", "euro", "percent", "numeric"

# Conditional cell styling — applied to all cells per column unless
# narrowed via ``styleConditions``.
cell_style = {
    "styleConditions": [
        {
            "condition": "params.value < 1045",
            "style": {"backgroundColor": "#ff9222"},
        }
    ]
}

drop_in_page = vm.Page(
    title="Sales table",
    components=[
        vm.AgGrid(
            id="sales_table",
            title="Country GDP detail",
            figure=dash_ag_grid(
                data_frame=df,
                columnDefs=column_defs,
                # Per-column defaults — applied to every column unless
                # the ``columnDefs`` entry overrides.
                defaultColDef={
                    "resizable": True,
                    "filter": True,
                    "sortable": True,
                },
                # Pagination is ON by default — disable for short tables.
                dashGridOptions={"pagination": False},
                # Sizing: "autoSize", "sizeToFit", "responsiveSizeToFit", or None.
                columnSize="responsiveSizeToFit",
            ),
        )
    ],
)


# ---------------------------------------------------------------------------
# Pattern 2 — Custom @capture("ag_grid")
# ---------------------------------------------------------------------------

from dash_ag_grid import AgGrid
from vizro.models.types import capture


@capture("ag_grid")
def my_custom_aggrid(chosen_columns: list[str], data_frame=None):
    """Return a ``dash_ag_grid.AgGrid`` object.

    Vizro will wrap the returned grid into the page layout. The
    ``data_frame`` keyword is supplied by Vizro at render time; any
    other kwargs (``chosen_columns`` here) become parameters that can
    be wired to ``vm.Parameter`` or filters.
    """
    defaults = {
        "className": "ag-theme-vizro",
        "defaultColDef": {
            "resizable": True,
            "sortable": True,
            "filter": True,
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
            "flex": 1,
            "minWidth": 70,
        },
    }
    return AgGrid(
        columnDefs=[{"field": col} for col in chosen_columns],
        rowData=data_frame.to_dict("records"),
        **defaults,
    )


custom_page = vm.Page(
    title="Sales table — custom",
    components=[
        vm.AgGrid(
            id="custom_ag_grid",
            title="Custom Dash AgGrid",
            figure=my_custom_aggrid(
                data_frame=df,
                chosen_columns=["country", "continent", "lifeExp", "pop", "gdpPercap"],
            ),
        )
    ],
)


# ---------------------------------------------------------------------------
# Gotchas (from the Vizro docs)
# ---------------------------------------------------------------------------
#
# - Date columns: dates must be ``yyyy-mm-dd`` strings OR pandas
#   datetime objects. Vizro auto-converts datetime columns to the
#   required string format on render — but if you do datetime
#   arithmetic in a custom loader, return ``.dt.strftime("%Y-%m-%d")``
#   so AG Grid renders them as dates rather than ints.
# - Pagination on by default — explicit ``dashGridOptions={"pagination": False}``
#   when the user wants the whole table at once.
# - Sticky headers only work reliably when the page is non-scrollable.
#   On long pages the header scrolls with the rest of the content.
# - Some AG Grid features (e.g. row grouping, master/detail) require
#   client-side callbacks that Vizro does not register by default. If
#   a column-level config "just doesn't work", switch to Pattern 2 and
#   inline the full ``dash_ag_grid.AgGrid`` you need.
# - If repeated Playwright walks reveal AG Grid integration bugs in
#   your Vizro version, **drop the AG Grid for that page and replace
#   it with the next-simplest visual** (KPI cards row, horizontal bar
#   chart, line chart). The design spec is authoritative, but Vizro
#   table integration is the most fragile component — substituting a
#   chart that conveys the same insight is the right call.


if __name__ == "__main__":
    Vizro().build(vm.Dashboard(pages=[drop_in_page, custom_page])).run()
