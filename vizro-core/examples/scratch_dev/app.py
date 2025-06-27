"""Dev app to try things out."""

from vizro.actions._update_control import update_control

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
    - 🔒(expected) It only works with the latest and unreleased Dash version.
        Test cases:
        (URL in the same order as control outputs)
        - http://localhost:8050/page_4?page_4_filter_species=b64_WyJ2ZXJzaWNvbG9yIl0&page_4_filter_sepal_width=b64_WzMsNC40XQ&page_4_dfp=b64_InZlcnNpY29sb3Ii
            - ✅Results: ["versicolor"], [3, 4.4], "versicolor"
        (different order)
        - http://localhost:8050/page_4?page_4_filter_sepal_width=b64_WzMsNC40XQ&page_4_filter_species=b64_WyJ2ZXJzaWNvbG9yIl0&page_4_dfp=b64_InZlcnNpY29sb3Ii
            - ✅Results: ["versicolor"], [3, 4.4], "versicolor"
        (missing species filter)
        - http://localhost:8050/page_4?page_4_filter_sepal_width=b64_WzMsNC40XQ&page_4_dfp=b64_InZlcnNpY29sb3Ii
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

    5.6 Test incorrect URL parameters:
    - ✅Confirm that the bug is not raised and that the page can be opened. Values should be ["ALL"] & [2, 4.4].
        Url should be updated to: b64_WzIsNC40XQ & b64_IkFMTCI
    - (URL with non base64 encoded value)
        - http://localhost:8050/page_2?page_2_filter_sepal_width=PLAIN_TEXT
        - http://localhost:8050/page_2?page_2_filter_species=PLAIN_TEXT
    - (URL with incorrect base64 encoded value)
        - http://localhost:8050/page_2?page_2_filter_sepal_width=b64_INCORRECT
        - http://localhost:8050/page_2?page_2_filter_species=b64_INCORRECT
    - (URL with missing query parameter value)
        - http://localhost:8050/page_2?page_2_filter_sepal_width=
        - http://localhost:8050/page_2?page_2_filter_species=
"""
import json
import base64

from dash import callback, dcc, Input, Output, exceptions

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.managers import data_manager
from vizro.tables import dash_ag_grid
from vizro.actions import filter_interaction


SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}

df = px.data.iris()


# def encode_to_base64(value):
#     json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
#     b64_bytes = base64.urlsafe_b64encode(json_bytes)
#     return f"b64_{b64_bytes.decode('utf-8').rstrip('=')}"


# TODO-CHECK: 1. Drill-through to Page-3 - [WORKS]
# @capture("action")
# def custom_drill_through_action(clicked_point):
#     species = clicked_point["points"][0]["customdata"][0]
#     return f"/page_3", f"?page_3_filter_species={encode_to_base64(species)}"


# TODO-CHECK: 2. Same page interaction over URL - [Doesn't work when the same point is clicked twice.]
# @capture("action")
# def same_page_interaction_over_url(clicked_point):
#     species = clicked_point["points"][0]["customdata"][0]
#     return f"?page_2_filter_species={encode_to_base64(species)}"


# TODO-CHECK: 3. Same page interaction over controls - [Doesn't work as expected, because filter-action is not clicked]
# @capture("action")
# def same_page_interaction_over_controls(clicked_point):
#     species = clicked_point["points"][0]["customdata"][0]
#     return [species]


# # TODO-CHECK: 4. Same page interaction over controls with dash callback - [WORKS]
# @callback(
#     Output("page_2_filter_selector_species", "value", allow_duplicate=True),
#     Input("page_2_graph", "clickData"),
#     prevent_initial_call=True,
# )
# def same_page_interaction_over_controls_dash_callback(click_data):
#     if click_data is None:
#         raise exceptions.PreventUpdate
#     species = click_data["points"][0]["customdata"][0]
#     return [species]


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


# TODO-CHECK: Update two controls at once - [WORKS, but only one filter action is triggered]
# @callback(
#     Output("page_2_filter_selector_species", "value", allow_duplicate=True),
#     Output("page_2_filter_selector_sepal_width", "value", allow_duplicate=True),
#     Input("page_2_button", "n_clicks"),
#     prevent_initial_call=True,
# )
# def update_two_controls(n_clicks):
#     if n_clicks is None:
#         raise exceptions.PreventUpdate
#     # Set the values for the two controls
#     return ["setosa", "versicolor"], [3, 4.4]


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
                update_control(
                    target="page_3_filter_species", lookup="points.0.customdata.0", trigger="page_2_graph.clickData"
                ),
                # f"/page_3", f"?page_3_filter_species={encode_to_base64(species)}"
                # vm.Action(
                #     # TODO-CHECK: Drill-through to Page-3
                #     function=custom_drill_through_action("page_2_graph.clickData"),
                #     outputs=["vizro_url_callback_nav.pathname", "vizro_url_callback_nav.search"],
                #     # TODO-CHECK: Same page interaction over URL
                #     # function=same_page_interaction_over_url("page_2_graph.clickData"),
                #     # outputs=["vizro_url_callback_nav.search"],
                #     # TODO-CHECK: Same page interaction over controls
                #     # function=same_page_interaction_over_controls("page_2_graph.clickData"),
                #     # outputs=["page_2_filter_selector_species.value"],
                # ),
            ],
        ),
        vm.Button(
            id="page_2_button",
            text="Update two controls at once",
            # TODO-CHECK: Update two controls at once - [Doesn't work as expected. URL is update, but filter action is not triggered]
            actions=[
                vm.Action(
                    function=(capture("action")(lambda: (["setosa", "versicolor"], [3, 4.4]))()),
                    outputs=[
                        "page_2_filter_selector_species.value",
                        "page_2_filter_selector_sepal_width.value",
                    ],
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
    app.dash.layout.children.append(dcc.Location(id="vizro_url", refresh="callback-nav"))

    app.run(debug=True, use_reloader=False)
