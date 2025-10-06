"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture

# TODO PP:
#  [DONE] Make PoC
#    [DONE] Make button
#    [DONE] Make vizro_controls_store
#    [DONE] Make js fun
#  [DONE] Make guardian existing for all filter/parameters
#  [DONE] Fix output OPL-trigger duplicate output issue.
#  [DONE] scratch-app add all selectors to all pages. [static, dynamic, url, hidden]
#    [DONE] Add set controls button and fix layout for all pages.
#    [DONE] Add a parameter
#  [DONE] Fix null originalValue added for p1_control_1_selector and maybe others
#  [DONE] Fix comments
#  [] Refactor code
#  [] Investigate should the just adjust the sync_url except adding a new clientside callback.
#  [] Fix it exists only if there are controls on the page.
#  [] unit tests
#  [] js tests
#  [] screenshot and other e2e tests
#  [] lint
#  [] Add changelog
#  [] Should we explain this feature in docs?
#  [] Should I adjust docs screenshots? Probably not worth it.


df = px.data.iris()
df["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(df), freq='D')
df["is_setosa"] = df["species"] == "setosa"

data_manager["dynamic_df"] = lambda: df


@capture("action")
def set_all_page_controls():
    return [
        "setosa", "setosa", ["setosa"], ["setosa"], 5.1, [5.1, 5.3], "2024-01-01", ["2024-01-01", "2024-01-10"], True,
        "petal_length"
    ] * 2


def _make_all_selectors(prefix_id: str, visible=True, show_in_url=False):
    return [
        vm.Filter(
            id=f"{prefix_id}_filter_1",
            column="species",
            targets=[f'{prefix_id}_graph'],
            selector=vm.RadioItems(id=f"{prefix_id}_filter_1_selector"),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Filter(
            id=f"{prefix_id}_filter_2",
            column="species",
            targets=[f'{prefix_id}_graph'],
            selector=vm.Dropdown(id=f"{prefix_id}_filter_2_selector", multi=False),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Filter(
            id=f"{prefix_id}_filter_3",
            column="species",
            targets=[f'{prefix_id}_graph'],
            selector=vm.Checklist(id=f"{prefix_id}_filter_3_selector"),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Filter(
            id=f"{prefix_id}_filter_4",
            column="species",
            targets=[f'{prefix_id}_graph'],
            selector=vm.Dropdown(id=f"{prefix_id}_filter_4_selector"),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Filter(
            id=f"{prefix_id}_filter_5",
            column="sepal_length",
            targets=[f'{prefix_id}_graph'],
            selector=vm.Slider(id=f"{prefix_id}_filter_5_selector"),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Filter(
            id=f"{prefix_id}_filter_6",
            column="sepal_length",
            targets=[f'{prefix_id}_graph'],
            selector=vm.RangeSlider(id=f"{prefix_id}_filter_6_selector"),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Filter(
            id=f"{prefix_id}_filter_7",
            column="date_column",
            targets=[f'{prefix_id}_graph'],
            selector=vm.DatePicker(id=f"{prefix_id}_filter_7_selector", range=False),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Filter(
            id=f"{prefix_id}_filter_8",
            column="date_column",
            targets=[f'{prefix_id}_graph'],
            selector=vm.DatePicker(id=f"{prefix_id}_filter_8_selector"),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Filter(
            id=f"{prefix_id}_filter_9",
            column="is_setosa",
            targets=[f'{prefix_id}_graph'],
            selector=vm.Switch(id=f"{prefix_id}_filter_9_selector"),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Parameter(
            id=f"{prefix_id}_filter_10",
            targets=[f'{prefix_id}_graph.x'],
            selector=vm.RadioItems(
                id=f"{prefix_id}_filter_10_selector",
                title="I'M A PARAMETER",
                options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
            ),
            visible=visible,
            show_in_url=show_in_url,
        ),
    ]


def _make_page_components(page_id: str, visible=True, show_in_url=False):
    return [
        vm.Button(
            text="Set controls",
            actions=vm.Action(
                function=set_all_page_controls(),
                outputs=[
                    *[f"{page_id}_static_filter_{i}" for i in range(1, 11)],
                    *[f"{page_id}_dynamic_filter_{i}" for i in range(1, 11)],
                ]
            )
        ),
        vm.Graph(
            id=f"{page_id}_static_graph",
            title="Static Graph",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")
        ),
        vm.Container(
            title="Dynamic selectors",
            components=[
                vm.Graph(
                    id=f"{page_id}_dynamic_graph",
                    title="Dynamic Graph",
                    figure=px.scatter("dynamic_df", x="sepal_width", y="sepal_length", color="species")
                ),
            ],
            controls=_make_all_selectors(prefix_id=f"{page_id}_dynamic", visible=visible, show_in_url=show_in_url)
        )
    ]


# ========== Page with all controls shown ==========

page_show_controls = vm.Page(
    id="page_1",
    title="All selectors page",
    layout=vm.Grid(grid=[[0], [1], [1], [1], [1], [2], [2], [2], [2], [2], [2]]),
    components=_make_page_components(page_id="p1"),
    controls=_make_all_selectors(prefix_id="p1_static")
)


# ========== Page with no controls ==========

page_no_controls = vm.Page(
    id="page_2",
    title="No controls",
    components=[
        vm.Graph(
            id="p2_static_graph",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")
        ),
        vm.Graph(
            id="p2_dynamic_graph",
            figure=px.scatter("dynamic_df", x="sepal_width", y="sepal_length", color="species")
        ),
    ],
)


# ========== Page with all controls hidden ==========

page_hidden_controls = vm.Page(
    id="page_3",
    title="All hidden selectors page",
    layout=vm.Grid(grid=[[0], [1], [1], [1], [1], [2], [2], [2], [2], [2], [2]]),
    components=_make_page_components(page_id="p3", visible=False),
    controls=_make_all_selectors(prefix_id="p3_static", visible=False)
)


# ========== Page with all controls in URL ==========

page_url_controls = vm.Page(
    id="page_4",
    title="All selectors in URL page",
    layout=vm.Grid(grid=[[0], [1], [1], [1], [1], [2], [2], [2], [2], [2], [2]]),
    components=_make_page_components(page_id="p4", show_in_url=True),
    controls=_make_all_selectors(prefix_id="p4_static", show_in_url=True)
)


# ========== Dashboard ==========

dashboard = vm.Dashboard(
    pages=[
        page_show_controls,
        page_no_controls,
        page_hidden_controls,
        page_url_controls
    ],
    navigation=vm.Navigation(nav_selector=vm.NavBar()),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
