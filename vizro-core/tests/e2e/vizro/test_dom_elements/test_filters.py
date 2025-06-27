import e2e.vizro.constants as cnst
import pytest
from e2e.vizro.checkers import (
    check_graph_is_loaded,
    check_selected_categorical_component,
    check_selected_dropdown,
    check_slider_value,
)
from e2e.vizro.navigation import clear_dropdown, page_select, select_dropdown_value
from e2e.vizro.paths import (
    categorical_components_value_path,
    dropdown_arrow_path,
    kpi_card_path,
    select_all_path,
    slider_value_path,
)
from e2e.vizro.waiters import graph_load_waiter
from hamcrest import assert_that, equal_to


def test_dropdown_select_all_value(dash_br):
    """Test interacts with Select All checkbox in dropdown.

    1. Click 'Select All'. It will clear all chosen options.
    2. Check how options in dropdown looks like.
    3. Click 'Select All'. It will make all options chosen.
    4. Check how options in dropdown looks like.
    """
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    # click dropdown arrow to open the list
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE), 1)
    # unselect 'Select All'
    dash_br.multiple_click(f"#{cnst.DROPDOWN_FILTER_FILTERS_PAGE}_select_all", 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        all_value=False,
        expected_selected_options=[],
        expected_unselected_options=["SelectAll", "setosa", "versicolor", "virginica"],
    )
    # select 'Select All'
    dash_br.multiple_click(f"#{cnst.DROPDOWN_FILTER_FILTERS_PAGE}_select_all", 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        all_value=True,
        expected_selected_options=["setosa", "versicolor", "virginica"],
        expected_unselected_options=[],
    )


def test_dropdown_options_value(dash_br):
    """Test interacts with options values in dropdown.

    1. Delete 'virginica' option.
    2. Check how options in dropdown looks like.
    3. Clear all chosen options and select 'setosa' only.
    4. Check how options in dropdown looks like.
    """
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    # delete last option 'virginica'
    dash_br.clear_input(f"div[id='{cnst.DROPDOWN_FILTER_FILTERS_PAGE}']")
    check_graph_is_loaded(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        all_value=False,
        expected_selected_options=["setosa", "versicolor"],
        expected_unselected_options=["SelectAll", "virginica"],
    )
    # clear dropdown
    clear_dropdown(dash_br, cnst.DROPDOWN_FILTER_FILTERS_PAGE)
    # choose one option 'setosa'
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE, value="setosa")
    check_graph_is_loaded(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(dropdown_arrow_path(cnst.DROPDOWN_FILTER_FILTERS_PAGE), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        all_value=False,
        expected_selected_options=["setosa"],
        expected_unselected_options=["SelectAll", "versicolor", "virginica"],
    )


def test_dropdown_persistence(dash_br):
    """Check that chosen values persistent after page reload."""
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    # delete last option 'virginica'
    dash_br.clear_input(f"div[id='{cnst.DROPDOWN_FILTER_FILTERS_PAGE}']")
    check_graph_is_loaded(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    page_select(dash_br, page_path=cnst.HOME_PAGE_PATH, page_name=cnst.HOME_PAGE)
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    dash_br.multiple_click(dropdown_arrow_path(cnst.DROPDOWN_FILTER_FILTERS_PAGE), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        all_value=False,
        expected_selected_options=["setosa", "versicolor"],
        expected_unselected_options=["SelectAll", "virginica"],
    )


@pytest.mark.parametrize(
    "filter_id",
    [cnst.CHECK_LIST_FILTER_FILTERS_PAGE, cnst.RADIO_ITEMS_FILTER_FILTERS_PAGE],
    ids=["checklist", "radio_items"],
)
def test_categorical_filters(dash_br, filter_id):
    """Test simple checklist and radio_items filters."""
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)

    # select 'setosa'
    dash_br.multiple_click(categorical_components_value_path(elem_id=filter_id, value=2), 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)


@pytest.mark.parametrize(
    "value_paths, select_all_status, options_value_status",
    [
        (
            [categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=2)],
            False,
            [
                {"value": 1, "selected": True, "value_name": "setosa"},
                {"value": 2, "selected": False, "value_name": "versicolor"},
                {"value": 3, "selected": True, "value_name": "virginica"},
            ],
        ),
        # TODO: Find the problem
        # (
        #     [
        #         select_all_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE),
        #         categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=3),
        #     ],
        #     False,
        #     [{"value": 1, "selected": False, "value_name": "setosa"},
        #      {"value": 2, "selected": False, "value_name": "versicolor"},
        #      {"value": 3, "selected": True, "value_name": "virginica"}],
        # ),
        (
            [
                categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=1),
                categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=2),
                categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=3),
            ],
            False,
            [
                {"value": 1, "selected": False, "value_name": "setosa"},
                {"value": 2, "selected": False, "value_name": "versicolor"},
                {"value": 3, "selected": False, "value_name": "virginica"},
            ],
        ),
        (
            [select_all_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE)],
            False,
            [
                {"value": 1, "selected": False, "value_name": "setosa"},
                {"value": 2, "selected": False, "value_name": "versicolor"},
                {"value": 3, "selected": False, "value_name": "virginica"},
            ],
        ),
        (
            [
                select_all_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE),
                select_all_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE),
            ],
            True,
            [
                {"value": 1, "selected": True, "value_name": "setosa"},
                {"value": 2, "selected": True, "value_name": "versicolor"},
                {"value": 3, "selected": True, "value_name": "virginica"},
            ],
        ),
    ],
    ids=[
        "unchecked one option",
        # "checked one option only",
        "unchecked all options",
        "unchecked 'Select All' only",
        "checked 'Select All' only",
    ],
)
def test_checklist(dash_br, value_paths, select_all_status, options_value_status):
    """Checks checklist with different options selected."""
    filter_id = cnst.CHECK_LIST_FILTER_FILTERS_PAGE
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    for path in value_paths:
        dash_br.multiple_click(path, 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    check_selected_categorical_component(
        dash_br,
        component_id=filter_id,
        select_all_status=select_all_status,
        checklist=True,
        options_value_status=options_value_status,
    )


def test_checklist_persistence(dash_br):
    """Check that chosen values persistent after page reload."""
    filter_id = cnst.CHECK_LIST_FILTER_FILTERS_PAGE
    page_select(
        dash_br,
        page_path=cnst.FILTERS_PAGE_PATH,
        page_name=cnst.FILTERS_PAGE,
    )
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, value=2), 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    page_select(dash_br, page_path=cnst.HOME_PAGE_PATH, page_name=cnst.HOME_PAGE)
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    check_selected_categorical_component(
        dash_br,
        component_id=filter_id,
        select_all_status=False,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )


def test_slider(dash_br):
    """Test simple slider filter."""
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)

    # select value '0.6'
    dash_br.multiple_click(slider_value_path(elem_id=cnst.SLIDER_FILTER_FILTERS_PAGE, value=2), 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    check_slider_value(dash_br, expected_end_value="0.6", elem_id=cnst.SLIDER_FILTER_FILTERS_PAGE)


@pytest.mark.xfail(reason="Should be fixed later in vizro by Petar")
# Right now is failing with the next error:
# AssertionError: Element number is '4', but expected number is '4.3'
def test_range_slider(dash_br):
    """Test simple range slider filter."""
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)

    # select min value '4.3'
    dash_br.multiple_click(slider_value_path(elem_id=cnst.RANGE_SLIDER_FILTER_FILTERS_PAGE, value=4), 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.SCATTER_GRAPH_ID)
    check_slider_value(
        dash_br, elem_id=cnst.RANGE_SLIDER_FILTER_FILTERS_PAGE, expected_start_value="4.3", expected_end_value="7"
    )


def test_dropdown_multi_false_homepage(dash_br):
    """Checks dropdown with multi=False."""
    graph_load_waiter(dash_br)

    # select 'versicolor'
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_FILTER_HOMEPAGEPAGE, value="versicolor")
    check_graph_is_loaded(dash_br, cnst.AREA_GRAPH_ID)


def test_dropdown_kpi_indicators_page(dash_br):
    """Test dropdown to filter kpi cards."""
    page_select(dash_br, page_name=cnst.KPI_INDICATORS_PAGE, graph_check=False)

    # wait for cards value is loaded and checking its values
    dash_br.wait_for_text_to_equal(kpi_card_path(), "67434")
    values = dash_br.find_elements(kpi_card_path())
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

    # select 'B' value
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_FILTER_KPI_PAGE, value="B")

    # wait for cards value is loaded and checking its values
    dash_br.wait_for_text_to_equal(kpi_card_path(), "6434")
    values = dash_br.find_elements(kpi_card_path())
    values_text = [value.text for value in values]
    assert_that(
        actual_or_assertion=values_text,
        matcher=equal_to(
            [
                "6434",
                "6434.0",
                "6434.0",
                "6553",
                "6434",
                "6434.0",
                "$6434.00",
                "6434€",
                "6434.0",
                "6434",
                "6553",
            ]
        ),
    )
