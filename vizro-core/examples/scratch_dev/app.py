import pandas as pd
import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
from vizro.actions import set_control
from vizro.models.types import capture
from vizro.managers import data_manager

df = px.data.iris()

df["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(df), freq="D")
df["is_setosa"] = df["species"] == "setosa"

data_manager["dynamic_df"] = lambda: df


page_1 = vm.Page(
    title="Buttons trigger set_control",
    layout=vm.Flex(),
    components=[
        vm.Button(
            text="Set setosa",
            actions=set_control(control="filter-id-1", value="setosa"),
        ),
        vm.Button(
            text="Set versicolor",
            actions=set_control(control="filter-id-1", value="versicolor"),
        ),
        vm.Button(
            text="Set virginica",
            actions=set_control(control="filter-id-1", value="virginica"),
        ),
        vm.Graph(
            id="graph-1",
            figure=px.scatter(
                df,
                x="sepal_width",
                y="sepal_length",
                color="species",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"},
            ),
        ),
    ],
    controls=[vm.Filter(id="filter-id-1", column="species", targets=["graph-1"])],
)

page_2 = vm.Page(
    title="Button resets the certain control",
    components=[
        vm.Button(
            text="Reset species filter",
            actions=set_control(control="filter-id-2", value="setosa"),
        ),
        vm.Graph(
            id="graph-2",
            figure=px.scatter(
                df,
                x="sepal_width",
                y="sepal_length",
                color="species",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"},
            ),
        ),
    ],
    controls=[
        vm.Filter(id="filter-id-2", column="species", selector=vm.RadioItems()),
        vm.Filter(id="filter-id-3", column="sepal_length"),
    ],
)


# ==== Page 3: Button sets all types of selectors ====

SET_SELECTORS_VALUES = [
    "versicolor",
    "versicolor",
    ["versicolor"],
    ["versicolor"],
    "petal_length",
]


def _make_all_selectors(prefix_id: str, visible=True, show_in_url=False):
    return [
        vm.Filter(
            id=f"{prefix_id}_filter_1",
            column="species",
            targets=[f"{prefix_id}_graph"],
            selector=vm.RadioItems(id=f"{prefix_id}_filter_1_selector"),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Filter(
            id=f"{prefix_id}_filter_2",
            column="species",
            targets=[f"{prefix_id}_graph"],
            selector=vm.Dropdown(id=f"{prefix_id}_filter_2_selector", multi=False),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Filter(
            id=f"{prefix_id}_filter_3",
            column="species",
            targets=[f"{prefix_id}_graph"],
            selector=vm.Checklist(id=f"{prefix_id}_filter_3_selector"),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Filter(
            id=f"{prefix_id}_filter_4",
            column="species",
            targets=[f"{prefix_id}_graph"],
            selector=vm.Dropdown(id=f"{prefix_id}_filter_4_selector"),
            visible=visible,
            show_in_url=show_in_url,
        ),
        vm.Parameter(
            id=f"{prefix_id}_filter_5",
            targets=[f"{prefix_id}_graph.x"],
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
            # This was the solution before set_control source from Button was available
            # actions=vm.Action(
            #     function=set_all_page_controls(),
            #     outputs=[
            #         *[f"{page_id}_static_filter_{i}" for i in range(1, 11)],
            #         *[f"{page_id}_dynamic_filter_{i}" for i in range(1, 11)],
            #     ],
            # ),
            actions=[
                set_control(control=f"{page_id}_static_filter_{i}", value=SET_SELECTORS_VALUES[i - 1])
                for i in range(1, 6)
            ]
            + [
                set_control(control=f"{page_id}_dynamic_filter_{i}", value=SET_SELECTORS_VALUES[i - 1])
                for i in range(1, 6)
            ],
        ),
        vm.Graph(
            id=f"{page_id}_static_graph",
            title="Static Graph",
            figure=px.scatter(
                df,
                x="sepal_width",
                y="sepal_length",
                color="species",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"},
            ),
        ),
        vm.Container(
            title="Dynamic selectors",
            components=[
                vm.Graph(
                    id=f"{page_id}_dynamic_graph",
                    title="Dynamic Graph",
                    figure=px.scatter(
                        "dynamic_df",
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"},
                    ),
                ),
            ],
            controls=_make_all_selectors(prefix_id=f"{page_id}_dynamic", visible=visible, show_in_url=show_in_url),
        ),
    ]


page_3 = vm.Page(
    title="Button sets different selectors",
    layout=vm.Grid(grid=[[0], [1], [1], [1], [1], [2], [2], [2], [2], [2], [2]]),
    components=_make_page_components(page_id="p1"),
    controls=_make_all_selectors(prefix_id="p1_static"),
)


dashboard = vm.Dashboard(pages=[page_1, page_2, page_3])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
