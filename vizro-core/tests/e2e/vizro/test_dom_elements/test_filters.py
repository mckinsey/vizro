import e2e.vizro.constants as cnst
import pytest
from e2e.vizro.checkers import (
    check_graph_is_loading,
    check_selected_checklist,
    check_selected_dropdown,
    check_slider_value,
)
from e2e.vizro.navigation import page_select
from e2e.vizro.paths import categorical_components_value_path, dropdown_arrow_path, select_all_path, slider_value_path
from e2e.vizro.waiters import graph_load_waiter
from hamcrest import assert_that, equal_to


def test_dropdown_select_all_value(dash_br):
    """Test interacts with Select All checkbox in dropdown.

    1. Click 'Select All'. It will clear all chosen options.
    2. Check how options in dropdown looks like.
    3. Click 'Select All'. It will make all options chosen.
    4. Check how options in dropdown looks like.
    """
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    # click dropdown arrow to open the list
    dash_br.multiple_click(dropdown_arrow_path(), 1)
    # unselect 'Select All'
    dash_br.multiple_click(select_all_path(elem_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(dropdown_arrow_path(), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        all_value=False,
        expected_selected_options=[],
        expected_unselected_options=["setosa", "versicolor", "virginica"],
    )
    # select 'Select All'
    dash_br.multiple_click(select_all_path(elem_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(dropdown_arrow_path(), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        all_value=True,
        expected_selected_options=["setosa", "versicolor", "virginica"],
        expected_unselected_options=[],
    )


def test_dropdown_options_values(dash_br):
    """Test interacts with options values in dropdown.

    1. Delete 'virginica' option.
    2. Check how options in dropdown looks like.
    3. Clear all chosen options and select 'setosa' only.
    4. Check how options in dropdown looks like.
    """
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    # delete last option 'virginica'
    dash_br.clear_input(f"#{cnst.DROPDOWN_FILTER_FILTERS_PAGE}")
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        all_value=False,
        expected_selected_options=["setosa", "versicolor"],
        expected_unselected_options=["virginica"],
    )
    # clear dropdown
    dash_br.clear_input(f"#{cnst.DROPDOWN_FILTER_FILTERS_PAGE}")
    dash_br.clear_input(f"#{cnst.DROPDOWN_FILTER_FILTERS_PAGE}")
    # choose one option 'setosa'
    dash_br.select_dcc_dropdown(f"#{cnst.DROPDOWN_FILTER_FILTERS_PAGE}", "setosa")
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(dropdown_arrow_path(), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        all_value=False,
        expected_selected_options=["setosa"],
        expected_unselected_options=["versicolor", "virginica"],
    )


def test_dropdown_persistence(dash_br):
    """Check that chosen values persistent after page reload."""
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    # delete last option 'virginica'
    dash_br.clear_input(f"#{cnst.DROPDOWN_FILTER_FILTERS_PAGE}")
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    page_select(dash_br, page_path=cnst.HOME_PAGE_PATH, page_name=cnst.HOME_PAGE, graph_id=cnst.AREA_GRAPH_ID)
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(dropdown_arrow_path(), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        all_value=False,
        expected_selected_options=["setosa", "versicolor"],
        expected_unselected_options=["virginica"],
    )


@pytest.mark.parametrize(
    "filter_id",
    [cnst.CHECK_LIST_FILTER_FILTERS_PAGE, cnst.RADIO_ITEMS_FILTER_FILTERS_PAGE],
    ids=["checklist", "radio_items"],
)
def test_categorical_filters(dash_br, filter_id):
    """Check if checklist and radio_items available and triggering graph reload."""
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(categorical_components_value_path(elem_id=filter_id, value=2), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)


@pytest.mark.parametrize(
    "value_paths, select_all_status, options_value_status",
    [
        (
            [categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=2)],
            False,
            [{"value": 1, "status": True}, {"value": 2, "status": False}, {"value": 3, "status": True}],
        ),
        (
            [
                select_all_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE),
                categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=3),
            ],
            False,
            [{"value": 1, "status": False}, {"value": 2, "status": False}, {"value": 3, "status": True}],
        ),
        (
            [
                categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=1),
                categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=2),
                categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=3),
            ],
            False,
            [{"value": 1, "status": False}, {"value": 2, "status": False}, {"value": 3, "status": False}],
        ),
        (
            [select_all_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE)],
            False,
            [{"value": 1, "status": False}, {"value": 2, "status": False}, {"value": 3, "status": False}],
        ),
        (
            [
                select_all_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE),
                select_all_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE),
            ],
            True,
            [{"value": 1, "status": True}, {"value": 2, "status": True}, {"value": 3, "status": True}],
        ),
    ],
    ids=[
        "unchecked one option",
        "checked one option only",
        "unchecked all options",
        "unchecked 'Select All' only",
        "checked 'Select All' only",
    ],
)
def test_checklist(dash_br, value_paths, select_all_status, options_value_status):
    """Checks checklist with different options selected."""
    filter_id = cnst.CHECK_LIST_FILTER_FILTERS_PAGE
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    for path in value_paths:
        dash_br.multiple_click(path, 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    check_selected_checklist(
        dash_br, checklist_id=filter_id, select_all_status=select_all_status, options_value_status=options_value_status
    )


def test_checklist_persistence(dash_br):
    """Check that chosen values persistent after page reload."""
    filter_id = cnst.CHECK_LIST_FILTER_FILTERS_PAGE
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=2), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    page_select(dash_br, page_path=cnst.HOME_PAGE_PATH, page_name=cnst.HOME_PAGE, graph_id=cnst.AREA_GRAPH_ID)
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    check_selected_checklist(
        dash_br,
        checklist_id=filter_id,
        select_all_status=False,
        options_value_status=[
            {"value": 1, "status": True},
            {"value": 2, "status": False},
            {"value": 3, "status": True},
        ],
    )


def test_slider(dash_br):
    """Checks if slider available and triggering graph reload. Also checks new slider value."""
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(slider_value_path(elem_id=cnst.SLIDER_FILTER_FILTERS_PAGE, value=2), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    check_slider_value(dash_br, expected_end_value="0.6", elem_id=cnst.SLIDER_FILTER_FILTERS_PAGE)


@pytest.mark.xfail(reason="Should be fixed later in vizro by Petar")
# Right now is failing with the next error:
# AssertionError: Element number is '4', but expected number is '4.3'
def test_range_slider(dash_br):
    """Checks if range_slider available and triggering graph reload. Also checks new range_slider values."""
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(slider_value_path(elem_id=cnst.RANGE_SLIDER_FILTER_FILTERS_PAGE, value=4), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    check_slider_value(
        dash_br, elem_id=cnst.RANGE_SLIDER_FILTER_FILTERS_PAGE, expected_start_value="4.3", expected_end_value="7"
    )


def test_dropdown_multi_false_homepage(dash_br):
    """Checks dropdown with multi=False."""
    graph_load_waiter(dash_br, graph_id=cnst.AREA_GRAPH_ID)
    dash_br.select_dcc_dropdown(f"#{cnst.DROPDOWN_FILTER_HOMEPAGE}", "virginica")
    check_graph_is_loading(dash_br, cnst.AREA_GRAPH_ID)


def test_dropdown_kpi_indicators_page(dash_br):
    """Checks filtering for KPI cards."""
    page_select(dash_br, page_path=cnst.KPI_INDICATORS_PAGE_PATH, page_name=cnst.KPI_INDICATORS_PAGE)
    dash_br.wait_for_text_to_equal(".card-body", "67434")
    values = dash_br.find_elements(".card-body")
    values_text = [value.text for value in values]
    assert_that(
        actual_or_assertion=values_text,
        matcher=equal_to(
            [
                "67434",
                "67434.0",
                "67434.0",
                "65553",
                "67434",
                "67434.0",
                "$67434.00",
                "67434€",
                "67434.0",
                "67434",
                "65553",
            ]
        ),
    )
    dash_br.select_dcc_dropdown(f"#{cnst.DROPDOWN_FILTER_KPI_PAGE}", "C")
    dash_br.wait_for_text_to_equal(".card-body", "34")
    values = dash_br.find_elements(".card-body")
    values_text = [value.text for value in values]
    assert_that(
        actual_or_assertion=values_text,
        matcher=equal_to(
            [
                "34",
                "34.0",
                "34.0",
                "53",
                "34",
                "34.0",
                "$34.00",
                "34€",
                "34.0",
                "34",
                "53",
            ]
        ),
    )
