import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_selected_categorical_component, check_selected_dropdown
from e2e.vizro.navigation import accordion_select, page_select
from e2e.vizro.paths import categorical_components_value_path, page_title_path, scatter_point_path


def test_sync_hidden_parameter_filters_graph_and_title(dash_br):
    """Filter syncs a hidden parameter that drives the graph title."""
    accordion_select(dash_br, accordion_name=cnst.SYNC_CONTROLS_ACCORDION)
    page_select(dash_br, page_name=cnst.SYNC_HIDDEN_PARAMETER_PAGE, graph_check=False)

    # Select the 'versicolor' in the radio items, which should update the graph title and legend text
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.SYNC_HIDDEN_PARAMETER_RADIO_ITEMS_ID, value=2), 1
    )

    # Wait for the graph title to update to 'versicolor'
    dash_br.wait_for_text_to_equal(".gtitle", "versicolor")
    # Wait for the legend text to update to 'versicolor'
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='versicolor']", "versicolor")


def test_sync_multiple_controls_same_page(dash_br):
    """A same-page mesh of three chained/cyclic filters all sync from one change and refresh every graph."""
    accordion_select(dash_br, accordion_name=cnst.SYNC_CONTROLS_ACCORDION)
    page_select(dash_br, page_name=cnst.SYNC_MULTIPLE_CONTROLS_SAME_PAGE, graph_check=False)

    # Select 'versicolor' on the first filter; it should sync the other two filters and refresh all three graphs.
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.SYNC_MULTIPLE_CONTROLS_RADIO_ITEMS_1_ID, value=2), 1
    )

    # All three radio filters now show versicolor selected (direct and transitive sync across the mesh).
    for radio_items_id in (
        cnst.SYNC_MULTIPLE_CONTROLS_RADIO_ITEMS_1_ID,
        cnst.SYNC_MULTIPLE_CONTROLS_RADIO_ITEMS_2_ID,
        cnst.SYNC_MULTIPLE_CONTROLS_RADIO_ITEMS_3_ID,
    ):
        check_selected_categorical_component(
            dash_br,
            component_id=radio_items_id,
            checklist=False,
            options_value_status=[
                {"value": 1, "selected": False, "value_name": "setosa"},
                {"value": 2, "selected": True, "value_name": "versicolor"},
                {"value": 3, "selected": False, "value_name": "virginica"},
            ],
        )
    # Every graph is filtered to versicolor, so its legend text shows versicolor.
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='versicolor']", "versicolor")


def test_sync_cross_page_applies_on_target_page_open(dash_br):
    """Cross-page filter sync applies when the target page is opened."""
    accordion_select(dash_br, accordion_name=cnst.SYNC_CONTROLS_ACCORDION)
    page_select(dash_br, page_name=cnst.SYNC_CROSS_PAGE_SOURCE_PAGE, graph_check=False)

    # Select the 'versicolor' in the radio items, which should update the legend text
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.SYNC_CROSS_PAGE_SOURCE_RADIO_ITEMS_ID, value=2), 1
    )
    # Wait for the legend text to update to 'versicolor' on the source page
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='versicolor']", "versicolor")

    page_select(dash_br, page_name=cnst.SYNC_CROSS_PAGE_TARGET_PAGE, graph_check=False)

    check_selected_categorical_component(
        dash_br,
        component_id=cnst.SYNC_CROSS_PAGE_TARGET_CHECKLIST_ID,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )
    # Wait for the legend text to update to 'versicolor' on the target page
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='versicolor']", "versicolor")


def test_sync_drill_through_sets_same_page_control_and_target_on_open(dash_br):
    """Drill-through with same-page target stays on source; cross-page value applies on target open."""
    accordion_select(dash_br, accordion_name=cnst.SYNC_CONTROLS_ACCORDION)
    page_select(dash_br, page_name=cnst.SYNC_DRILL_THROUGH_SOURCE_PAGE, graph_check=False)

    # Select the 'versicolor' in the scatter plot, which should update the graph legend text
    dash_br.click_at_coord_fractions(scatter_point_path(cnst.SYNC_DRILL_THROUGH_SOURCE_GRAPH_ID, point_number=20), 0, 0)
    dash_br.wait_for_text_to_equal(page_title_path(), cnst.SYNC_DRILL_THROUGH_SOURCE_PAGE)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.SYNC_DRILL_THROUGH_SOURCE_DROPDOWN_ID,
        expected_selected_options=["versicolor"],
        multi=False,
    )
    # Wait for the legend text to update to 'versicolor' on the source page
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='versicolor']", "versicolor")

    page_select(dash_br, page_name=cnst.SYNC_DRILL_THROUGH_TARGET_PAGE, graph_check=False)

    check_selected_categorical_component(
        dash_br,
        component_id=cnst.SYNC_DRILL_THROUGH_TARGET_RADIO_ITEMS_ID,
        checklist=False,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )
    # Wait for the legend text to update to 'versicolor' on the target page
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='versicolor']", "versicolor")
