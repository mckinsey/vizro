"""Dev app to try things out."""

"""
Test cases:
1. When page is opened without the URL parameter:
    1.1. The control should default to their persisted values (if persist in the storage) or initial server values.
    1.2. If the control is show_in_url=True it should overwrite the URL.
2. When control is changed:
    2.1. The URL should be updated with the new control values.
3. When page is opened with the URL parameter:
    3.1. If the control is show_in_url=True, its should reflect the value from the URL.
    3.2. 🔒Affected control should update the persistence storage.
"""


"""
TODO-FOR-REVIEWER: Manual testing steps for sync URL-controls:


1. Page-1: No URL Controls
    - Run the app and navigate to Page-1: http://localhost:8050/
    - ✅ Confirm: This page does NOT contain any `show_in_url` controls.

2. Page-2: URL-Synced Controls (Dropdown + RangeSlider)
    2.1 Verify initial state:
        - Navigate to Page-2
        - Controls should default to ["ALL"] & [2, 4.4]
        - ✅ Confirm: URL reflects these values: IkFMTCI & WzIsNC40XQ

    2.2 Change control values:
        - Set controls to ["setosa", "versicolor"] & [3, 4.4]
        - ✅ Confirm: URL updates accordingly. WyJzZXRvc2EiLCJ2ZXJzaWNvbG9yIl0 & WzMsNC40XQ

    2.3 Refresh the page for couple of times:
        - ✅ Confirm: Selected values persist after refresh (state is preserved from URL).

    2.4 Copy and paste URL into a new tab:
        - ✅ Confirm: Page loads with correct filter state applied (["setosa", "versicolor"], & [3, 4.4])
            - ⚠️ RangeSlider number inputs above currently don't work correctly [2, 4.4] is set but should be [3, 4.4].
        - ✅ Confirm: URL reflects the same state as before copying.

    2.5 Navigate to Page-1 and back to Page-2:
        - ✅ Confirm: Values are still ["setosa", "versicolor"] & [3, 4.4]
            - 🔒(expected) It only works with the latest and unreleased Dash version.

3. Page-3:
    - Navigate to Page-3
    - ✅ Confirm: Values appear as ["ALL", 2]
    - ✅ Confirm: URL reflects these values: WyJBTEwiXQ & Mg

4. Drill-Through Test from Page-2
    - Go back to Page-2
    - Click the "versicolor" point on the graph

    4.1 Check redirection:
        - ✅ Confirm: Values are ["versicolor"] & 2
        - ✅ Confirm: URL updates to Page-3 with filter set to InZlcnNpY29sb3Ii -> (["versicolor"])

    4.2 Navigate to Page-1 and back to Page-3:
    - ✅ Confirm: Values are still ["versicolor"] & 2
        - 🔒(expected) It only works with the latest and unreleased Dash version.


5. Page-4: Dynamic Filters, DFP, and AgGrid Interaction
    - Navigate to Page-4 (testbed for dynamic filter, DFP and AgGrid filter interaction)

    5.1 Change:
        - DFP -> "versicolor",
        - species filter to ["versicolor"]
        - RangeSlider to [3, 4.4]

    5.2 Refresh the page:
        - ✅ Confirm: Values are still from URL: ["versicolor"], [3, 4.4], and DFP is "versicolor"
            - 🔒(expected) It only works with the latest and unreleased Dash version.

    5.3. Apply filter interaction from AgGrid (by selecting some value from the "Sepal_length" column):
        - ✅ Confirm: Graph updates

    5.4 Copy and paste URL into a new tab:
        - ✅ Confirm: Filters/parameters are applied from URL
        - Note: Grid interaction is not currently reflected in the URL, New "interact" action will solve that.

    5.5 Test order of URL parameters (Open each link in the new browser tab + Navigate to Page-1 and back to Page-4):
        Test cases:
        (URL in the same order as control outputs)
        - http://localhost:8050/page_4?page_4_filter_species=WyJ2ZXJzaWNvbG9yIl0&page_4_filter_sepal_width=WzMsNC40XQ&page_4_dfp=InZlcnNpY29sb3Ii
            - ✅Results: ["versicolor"], [3, 4.4], "versicolor"
        (different order)
        - http://localhost:8050/page_4?page_4_filter_sepal_width=WzMsNC40XQ&page_4_filter_species=WyJ2ZXJzaWNvbG9yIl0&page_4_dfp=InZlcnNpY29sb3Ii
            - ✅Results: ["versicolor"], [3, 4.4], "versicolor"
        (missing species filter)
        - http://localhost:8050/page_4?page_4_filter_sepal_width=WzMsNC40XQ&page_4_dfp=InZlcnNpY29sb3Ii
            - ✅Results: ["ALL"], [3, 4.4], "versicolor"
            - ✅Confirm that the `page_4_filter_species=WyJBTEwiXQ` is added to the URL.
        (unknown query parameter ID)
        - http://localhost:8050/page_4?UNKNOWN=InZlcnNpY29sb3Ii
            - ✅Results: ["ALL"], [2.3, 4.4], "setosa"
            - ✅Confirm that the `UNKNOWN` still exists in the URL.
            - ✅Confirm that the URL contains all other controls.
            - ✅Confirm that the changing the control neither page refresh does not remove UNKNOWN from the URL.
            - ❗the UNKNOWN parameter is not removed from the URL when navigating to Page-1 and back to Page-4.
        (unknown query parameter ID with value that is not base64 encoded)
        - http://localhost:8050/page_4?UNKNOWN=asd
            - ✅Confirm that the bug is not raised and that the page can be opened.
"""
from dash import dcc
import json
import base64

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.managers import data_manager
from vizro.tables import dash_ag_grid
from vizro.actions import filter_interaction


SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}

df = px.data.iris()


def encode_to_base64(value):
    json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
    b64_bytes = base64.urlsafe_b64encode(json_bytes)
    return b64_bytes.decode("utf-8").rstrip("=")


@capture("action")
def custom_drill_through_action(clicked_point):
    species = clicked_point["points"][0]["customdata"][0]
    return f"/page_3", f"?page_3_filter_species={encode_to_base64(species)}"


page_1 = vm.Page(
    title="Page_1",
    components=[
        vm.Graph(
            id="page_1_graph",
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
    ],
    controls=[
        vm.Filter(id="page_1_filter", column="species"),
    ],
)


page_2 = vm.Page(
    title="Page_2",
    components=[
        vm.Graph(
            id="page_2_graph",
            title="Click the points to trigger the drill-throgh on Page-3",
            figure=px.scatter(
                df,
                x="petal_width",
                y="petal_length",
                color="species",
                custom_data=["species"],
                color_discrete_map=SPECIES_COLORS,
            ),
            actions=[
                vm.Action(
                    function=custom_drill_through_action("page_2_graph.clickData"),
                    outputs=["vizro_url_callback_nav.pathname", "vizro_url_callback_nav.search"],
                )
            ],
        ),
    ],
    controls=[
        vm.Filter(
            id="page_2_filter_species",
            column="species",
            show_in_url=True,
            selector=vm.Dropdown(id="page_2_filter_selector_species"),
        ),
        vm.Filter(
            id="page_2_filter_sepal_width",
            column="sepal_width",
            show_in_url=True,
            selector=vm.RangeSlider(id="page_2_filter_selector_sepal_width"),
        ),
    ],
)

page_3 = vm.Page(
    title="Page_3",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    id="page_3_graph",
                    figure=px.scatter(
                        df, x="petal_length", y="petal_width", color="species", color_discrete_map=SPECIES_COLORS
                    ),
                ),
            ],
            controls=[
                vm.Filter(
                    id="page_3_filter_sepal_width",
                    column="sepal_width",
                    show_in_url=True,
                    selector=vm.Slider(id="page_3_filter_selector_sepal_width"),
                ),
                vm.Filter(
                    id="page_3_filter_species",
                    column="species",
                    show_in_url=True,
                    selector=vm.Dropdown(id="page_3_filter_selector_species"),
                ),
            ],
        )
    ],
)

data_manager["dy_df"] = lambda species="setosa": df[df["species"] == species]

page_4 = vm.Page(
    title="Page_4",
    components=[
        vm.Container(
            title="TEST: Dynamic Filter / DF Parameter / AgGrid filter interaction",
            components=[
                vm.AgGrid(
                    id="page_4_aggrid",
                    figure=dash_ag_grid(data_frame="dy_df"),
                    actions=[filter_interaction(targets=["page_4_graph"])],
                ),
                vm.Graph(
                    id="page_4_graph",
                    figure=px.scatter(
                        "dy_df", x="petal_length", y="petal_width", color="species", color_discrete_map=SPECIES_COLORS
                    ),
                ),
            ],
        )
    ],
    controls=[
        vm.Filter(
            id="page_4_filter_species",
            column="species",
            show_in_url=True,
            selector=vm.Checklist(id="page_4_filter_selector_species"),
        ),
        vm.Filter(
            id="page_4_filter_sepal_width",
            column="sepal_width",
            show_in_url=True,
            selector=vm.RangeSlider(id="page_4_filter_selector_sepal_width"),
        ),
        vm.Parameter(
            id="page_4_dfp",
            targets=["page_4_aggrid.data_frame.species", "page_4_graph.data_frame.species"],
            show_in_url=True,
            selector=vm.RadioItems(
                id="page_4_dfp_selector", title="DFP:", options=["setosa", "versicolor", "virginica"]
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4])

if __name__ == "__main__":
    app = Vizro().build(dashboard)

    # To enable custom drill-through actio)
    app.dash.layout.children.append(dcc.Location(id="vizro_url_callback_nav", refresh="callback-nav"))

    app.run(debug=True, use_reloader=False)
