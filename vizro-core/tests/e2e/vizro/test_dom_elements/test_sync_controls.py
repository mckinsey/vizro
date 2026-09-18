import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_selected_categorical_component, check_selected_dropdown
from e2e.vizro.navigation import accordion_select, page_select
from e2e.vizro.paths import categorical_components_value_path, page_title_path, scatter_point_path

_SPECIES_OPTIONS = [
    {"value": 1, "selected": False, "value_name": "setosa"},
    {"value": 2, "selected": True, "value_name": "versicolor"},
    {"value": 3, "selected": False, "value_name": "virginica"},
]


def _open_sync_controls_accordion(dash_br):
    accordion_select(dash_br, accordion_name=cnst.SYNC_CONTROLS_ACCORDION)


def _open_sync_hidden_parameter_page(dash_br):
    _open_sync_controls_accordion(dash_br)
    page_select(dash_br, page_name=cnst.SYNC_HIDDEN_PARAMETER_PAGE, graph_check=False)


def _open_sync_cross_page_source_page(dash_br):
    _open_sync_controls_accordion(dash_br)
    page_select(dash_br, page_name=cnst.SYNC_CROSS_PAGE_SOURCE_PAGE, graph_check=False)


def _open_sync_cross_page_target_page(dash_br):
    page_select(dash_br, page_name=cnst.SYNC_CROSS_PAGE_TARGET_PAGE, graph_check=False)


def _open_sync_drill_through_source_page(dash_br):
    _open_sync_controls_accordion(dash_br)
    page_select(dash_br, page_name=cnst.SYNC_DRILL_THROUGH_SOURCE_PAGE, graph_check=False)


def _open_sync_drill_through_target_page(dash_br):
    page_select(dash_br, page_name=cnst.SYNC_DRILL_THROUGH_TARGET_PAGE, graph_check=False)


def test_sync_hidden_parameter_filters_graph_and_title(dash_br):
    """Filter syncs a hidden parameter that drives the graph title."""
    _open_sync_hidden_parameter_page(dash_br)

    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.SYNC_HIDDEN_PARAMETER_RADIO_ITEMS_ID, value=2), 1
    )

    dash_br.wait_for_text_to_equal(".gtitle", "versicolor")
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='versicolor']", "versicolor")


def test_sync_cross_page_applies_on_target_page_open(dash_br):
    """Cross-page filter sync applies when the target page is opened."""
    _open_sync_cross_page_source_page(dash_br)

    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.SYNC_CROSS_PAGE_SOURCE_RADIO_ITEMS_ID, value=2), 1
    )
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='versicolor']", "versicolor")

    _open_sync_cross_page_target_page(dash_br)

    check_selected_categorical_component(
        dash_br,
        component_id=cnst.SYNC_CROSS_PAGE_TARGET_CHECKLIST_ID,
        checklist=True,
        options_value_status=_SPECIES_OPTIONS,
    )
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='versicolor']", "versicolor")


def test_sync_drill_through_sets_same_page_control_and_target_on_open(dash_br):
    """Drill-through with same-page target stays on source; cross-page value applies on target open."""
    _open_sync_drill_through_source_page(dash_br)

    dash_br.click_at_coord_fractions(
        scatter_point_path(cnst.SYNC_DRILL_THROUGH_SOURCE_GRAPH_ID, point_number=20), 0, 0
    )

    dash_br.wait_for_text_to_equal(page_title_path(), cnst.SYNC_DRILL_THROUGH_SOURCE_PAGE)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.SYNC_DRILL_THROUGH_SOURCE_DROPDOWN_ID,
        expected_selected_options=["versicolor"],
        multi=False,
    )
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='versicolor']", "versicolor")

    _open_sync_drill_through_target_page(dash_br)

    check_selected_categorical_component(
        dash_br,
        component_id=cnst.SYNC_DRILL_THROUGH_TARGET_RADIO_ITEMS_ID,
        checklist=False,
        options_value_status=_SPECIES_OPTIONS,
    )
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='versicolor']", "versicolor")
