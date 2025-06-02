import e2e.vizro.constants as cnst
import pytest
from e2e.vizro.checkers import check_graph_is_loading, check_slider_value
from e2e.vizro.navigation import page_select, select_dropdown_value
from e2e.vizro.paths import categorical_components_value_path, graph_axis_value_path, slider_value_path


def test_dropdown(dash_br):
    """Test simple dropdown filter."""
    page_select(
        dash_br, page_path=cnst.FILTERS_INSIDE_CONTAINERS_PAGE_PATH, page_name=cnst.FILTERS_INSIDE_CONTAINERS_PAGE
    )

    # select 'setosa'
    select_dropdown_value(dash_br, value=2, dropdown_id=cnst.DROPDOWN_INSIDE_CONTAINERS)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_INSIDE_CONTAINER)


@pytest.mark.parametrize(
    "filter_id",
    [cnst.CHECK_LIST_INSIDE_CONTAINERS, cnst.RADIO_ITEMS_INSIDE_CONTAINERS],
    ids=["checklist", "radio_items"],
)
def test_categorical_filters(dash_br, filter_id):
    """Test simple checklist and radio_items filters."""
    page_select(
        dash_br, page_path=cnst.FILTERS_INSIDE_CONTAINERS_PAGE_PATH, page_name=cnst.FILTERS_INSIDE_CONTAINERS_PAGE
    )

    # select 'setosa'
    dash_br.multiple_click(categorical_components_value_path(elem_id=filter_id, value=2), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_INSIDE_CONTAINER)


def test_slider(dash_br):
    """Test simple slider filter."""
    page_select(
        dash_br, page_path=cnst.FILTERS_INSIDE_CONTAINERS_PAGE_PATH, page_name=cnst.FILTERS_INSIDE_CONTAINERS_PAGE
    )

    # select value '0.6'
    dash_br.multiple_click(slider_value_path(elem_id=cnst.SLIDER_INSIDE_CONTAINERS, value=2), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_INSIDE_CONTAINER)
    check_slider_value(dash_br, expected_end_value="0.6", elem_id=cnst.SLIDER_INSIDE_CONTAINERS)


@pytest.mark.xfail(reason="Should be fixed later in vizro by Petar")
# Right now is failing with the next error:
# AssertionError: Element number is '4', but expected number is '4.3'
def test_range_slider(dash_br):
    """Test simple range slider filter."""
    page_select(
        dash_br, page_path=cnst.FILTERS_INSIDE_CONTAINERS_PAGE_PATH, page_name=cnst.FILTERS_INSIDE_CONTAINERS_PAGE
    )

    # select min value '4.3'
    dash_br.multiple_click(slider_value_path(elem_id=cnst.RANGE_SLIDER_INSIDE_CONTAINERS, value=4), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_INSIDE_CONTAINER)
    check_slider_value(
        dash_br, elem_id=cnst.RANGE_SLIDER_INSIDE_CONTAINERS, expected_start_value="4.3", expected_end_value="7"
    )


def test_range_datepicker(dash_br):
    page_select(
        dash_br, page_path=cnst.FILTERS_INSIDE_CONTAINERS_PAGE_PATH, page_name=cnst.FILTERS_INSIDE_CONTAINERS_PAGE
    )

    # open datepicker calendar and choose dates from 10 to 26 January 2024
    dash_br.multiple_click(f'button[id="{cnst.RANGE_DATEPICKER_INSIDE_CONTAINERS}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.multiple_click('button[aria-label="10 January 2024"]', 1)
    dash_br.multiple_click('button[aria-label="26 January 2024"]', 1)
    dash_br.wait_for_text_to_equal(f'button[id="{cnst.RANGE_DATEPICKER_INSIDE_CONTAINERS}"]', "2024/01/10 – 2024/01/26")  # noqa: RUF001

    # Check x axis min value is '4.4'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.SCATTER_INSIDE_CONTAINER, axis_value_number="7", axis_value="4.4"),
        "4.4",
    )
