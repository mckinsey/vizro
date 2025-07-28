import e2e.vizro.constants as cnst
import pytest
from e2e.asserts import decode_url_params, encode_url_params, get_url_params, param_to_url
from e2e.vizro.checkers import check_selected_categorical_component, check_selected_dropdown
from e2e.vizro.navigation import accordion_select, clear_dropdown, page_select, select_dropdown_value
from e2e.vizro.paths import (
    categorical_components_value_path,
    dropdown_arrow_path,
    slider_value_path,
    switch_path_using_filter_control_id,
)
from hamcrest import assert_that, equal_to


def test_url_filters_encoding_and_page_refresh(dash_br):
    """Verifies that URL params for filters are correctly encoded and restored after a page refresh."""
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    # select 'virginica' for dropdown and 'versicolor' for radio_items
    clear_dropdown(dash_br, dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE)
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE, value="virginica")
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.RADIO_ITEMS_FILTER_FILTERS_PAGE, value=2), 1, delay=0.1
    )
    # check correct urls params
    selected_params = {cnst.DROPDOWN_FILTER_CONTROL_ID: ["virginica"], cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "versicolor"}
    enc_data = encode_url_params(selected_params, apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS)
    url_params_dict = get_url_params(dash_br)
    assert_that(url_params_dict, equal_to(enc_data))
    # refresh the page
    dash_br.driver.refresh()
    # check url params still the same
    url_params_dict = get_url_params(dash_br)
    assert_that(url_params_dict, equal_to(enc_data))


def test_url_filters_decoding_and_navigate_to_page(dash_br):
    """Verifies that URL params for filters could be correctly decoded and restored after a page refresh."""
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    # select 'virginica' for dropdown and 'versicolor' for radio_items
    clear_dropdown(dash_br, dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE)
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE, value="virginica")
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.RADIO_ITEMS_FILTER_FILTERS_PAGE, value=2), 1, delay=0.1
    )
    # check correct urls params
    selected_params = {cnst.DROPDOWN_FILTER_CONTROL_ID: ["virginica"], cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "versicolor"}
    url_params_dict = get_url_params(dash_br)
    dec_data = decode_url_params(url_params_dict, apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS)
    assert_that(dec_data, equal_to(selected_params))
    # navigate to another page and back
    page_select(dash_br, page_path=cnst.PARAMETERS_PAGE_PATH, page_name=cnst.PARAMETERS_PAGE)
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    # check url params still the same
    url_params_dict = get_url_params(dash_br)
    dec_data = decode_url_params(url_params_dict, apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS)
    assert_that(dec_data, equal_to(selected_params))


@pytest.mark.parametrize(
    "dash_br_driver, expected_decoded_map, dropdown_values, selected_radio_items_values",
    [
        (
            {
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"""{
                    param_to_url(
                        decoded_map={cnst.DROPDOWN_FILTER_CONTROL_ID: ["setosa", "versicolor", "virginica"]},
                        apply_on_keys=[cnst.DROPDOWN_FILTER_CONTROL_ID],
                    )
                }""",
            },
            {
                cnst.DROPDOWN_FILTER_CONTROL_ID: ["setosa", "versicolor", "virginica"],
                cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa",
            },
            [["setosa", "versicolor", "virginica"], []],
            ["setosa"],
        ),
        (
            {
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"""{
                    param_to_url(
                        decoded_map={
                            cnst.DROPDOWN_FILTER_CONTROL_ID: ["versicolor", "virginica"],
                            cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "versicolor",
                        },
                        apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS,
                    )
                }""",
            },
            {
                cnst.DROPDOWN_FILTER_CONTROL_ID: ["versicolor", "virginica"],
                cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "versicolor",
            },
            [["versicolor", "virginica"], ["SelectAll", "setosa"]],
            ["versicolor"],
        ),
        (
            {
                "path": f"{cnst.FILTERS_PAGE_PATH}?{cnst.RADIO_ITEMS_FILTER_CONTROL_ID}=b64_InZlcnNpY29sb",
            },  # invalid value
            {
                cnst.DROPDOWN_FILTER_CONTROL_ID: ["setosa", "versicolor", "virginica"],
                cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa",
            },
            [["setosa", "versicolor", "virginica"], []],
            ["setosa"],
        ),
        (
            {
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{cnst.DROPDOWN_FILTER_CONTROL_ID}=&{cnst.RADIO_ITEMS_FILTER_CONTROL_ID}=",
            },  # empty values
            {
                cnst.DROPDOWN_FILTER_CONTROL_ID: ["setosa", "versicolor", "virginica"],
                cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa",
            },
            [["setosa", "versicolor", "virginica"], []],
            ["setosa"],
        ),
        (
            {
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"""{
                    param_to_url(
                        decoded_map={cnst.DROPDOWN_FILTER_CONTROL_ID: ["virginica"]},
                        apply_on_keys=cnst.DROPDOWN_FILTER_CONTROL_ID,
                    )
                }&"""
                f"{cnst.RADIO_ITEMS_FILTER_CONTROL_ID}=InZpcmdpbmljYSI",
            },  # valid + invalid values
            {
                cnst.DROPDOWN_FILTER_CONTROL_ID: ["virginica"],
                cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa",
            },
            [["virginica"], ["SelectAll", "setosa", "versicolor"]],
            ["setosa"],
        ),
    ],
    indirect=["dash_br_driver"],
    ids=[
        "only dropdown value in url",
        "dropdown + radio_items values in url",
        "invalid value",
        "empty values",
        "valid + invalid values",
    ],
)
def test_different_url_parameters(dash_br_driver, expected_decoded_map, dropdown_values, selected_radio_items_values):
    """Verifies different URL params combinations and that controls has correct values according to it."""
    params_dict_simple = get_url_params(dash_br_driver)
    assert_that(
        params_dict_simple,
        equal_to(encode_url_params(decoded_map=expected_decoded_map, apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS)),
    )
    # radio_items values calculation
    radio_items_values = [
        {"value": 1, "selected": False, "value_name": "setosa"},
        {"value": 2, "selected": False, "value_name": "versicolor"},
        {"value": 3, "selected": False, "value_name": "virginica"},
    ]
    for item in radio_items_values:
        if item["value_name"] in selected_radio_items_values:
            item["selected"] = True
        else:
            item["selected"] = False
    # check that radio_items control have correct values
    check_selected_categorical_component(
        dash_br_driver,
        component_id=cnst.RADIO_ITEMS_FILTER_FILTERS_PAGE,
        options_value_status=radio_items_values,
    )
    # check that dropdown control have correct values
    dash_br_driver.multiple_click(dropdown_arrow_path(cnst.DROPDOWN_FILTER_FILTERS_PAGE), 1)
    check_selected_dropdown(
        dash_br_driver,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        expected_selected_options=dropdown_values[0],
        expected_unselected_options=dropdown_values[1],
    )


def test_url_params_encoding_and_page_refresh(dash_br):
    """Verifies that URL params for parameters are correctly encoded and restored after a page refresh."""
    page_select(dash_br, page_path=cnst.PARAMETERS_PAGE_PATH, page_name=cnst.PARAMETERS_PAGE)
    # select 0.6 for slider and [4, 7] for range_slider
    dash_br.multiple_click(slider_value_path(elem_id=cnst.SLIDER_PARAMETERS, value=3), 1)
    dash_br.multiple_click(slider_value_path(elem_id=cnst.RANGE_SLIDER_PARAMETERS, value=4), 1, delay=0.1)
    # check correct urls params
    selected_params = {cnst.SLIDER_PARAM_CONTROL_ID: 0.4, cnst.RANGE_SLIDER_PARAM_CONTROL_ID: [4, 7]}
    enc_data = encode_url_params(selected_params, apply_on_keys=cnst.PARAMS_PAGE_APPLY_ON_KEYS)
    url_params_dict = get_url_params(dash_br)
    assert_that(url_params_dict, equal_to(enc_data))
    # refresh the page
    dash_br.driver.refresh()
    # check url params still the same
    url_params_dict = get_url_params(dash_br)
    assert_that(url_params_dict, equal_to(enc_data))


def test_url_params_decoding_and_navigate_to_page(dash_br):
    """Verifies that URL params for parameters could be correctly decoded and restored after a page refresh."""
    page_select(dash_br, page_path=cnst.PARAMETERS_PAGE_PATH, page_name=cnst.PARAMETERS_PAGE)
    # select 0.8 for slider and [6, 8] for range_slider
    dash_br.multiple_click(slider_value_path(elem_id=cnst.SLIDER_PARAMETERS, value=5), 1)
    dash_br.multiple_click(slider_value_path(elem_id=cnst.RANGE_SLIDER_PARAMETERS, value=3), 1, delay=0.1)
    # check correct urls params
    selected_params = {cnst.SLIDER_PARAM_CONTROL_ID: 0.8, cnst.RANGE_SLIDER_PARAM_CONTROL_ID: [6, 8]}
    url_params_dict = get_url_params(dash_br)
    dec_data = decode_url_params(url_params_dict, apply_on_keys=cnst.PARAMS_PAGE_APPLY_ON_KEYS)
    assert_that(dec_data, equal_to(selected_params))
    # navigate to another page and back
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    page_select(dash_br, page_path=cnst.PARAMETERS_PAGE_PATH, page_name=cnst.PARAMETERS_PAGE)
    # check url params still the same
    url_params_dict = get_url_params(dash_br)
    dec_data = decode_url_params(url_params_dict, apply_on_keys=cnst.PARAMS_PAGE_APPLY_ON_KEYS)
    assert_that(dec_data, equal_to(selected_params))


def test_url_params_encoding_and_page_refresh_checklist(dash_br):
    """Verifies that URL params for checklist are correctly encoded and restored after a page refresh."""
    page_select(
        dash_br, page_path=cnst.FILTERS_INSIDE_CONTAINERS_PAGE_PATH, page_name=cnst.FILTERS_INSIDE_CONTAINERS_PAGE
    )
    # unselect 'setosa'
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.CHECK_LIST_FILTERS_CONTAINERS_CONTROL_ID, value=2), 1, delay=0.1
    )
    # check correct urls params
    selected_params = {cnst.CHECK_LIST_FILTERS_CONTAINERS_CONTROL_ID: ["versicolor", "virginica"]}
    enc_data = encode_url_params(selected_params, apply_on_keys=cnst.CHECK_LIST_FILTERS_CONTAINERS_CONTROL_ID)
    url_params_dict = get_url_params(dash_br)
    assert_that(url_params_dict, equal_to(enc_data))
    # refresh the page
    dash_br.driver.refresh()
    # check url params still the same
    url_params_dict = get_url_params(dash_br)
    assert_that(url_params_dict, equal_to(enc_data))


def test_url_params_encoding_and_page_refresh_datepicker(dash_br):
    """Verifies that URL params for datepicker are correctly encoded and restored after a page refresh."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DATEPICKER_PAGE,
    )
    # open datepicker calendar and choose dates from 17 to 18 May 2016
    dash_br.multiple_click(f'button[id="{cnst.DATEPICKER_RANGE_ID}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.multiple_click('button[aria-label="17 May 2016"]', 1)
    dash_br.multiple_click('button[aria-label="18 May 2016"]', 1)
    # check correct urls params
    selected_params = {cnst.DATEPICKER_FILTER_CONTROL_ID: ["2016-05-17", "2016-05-18"]}
    enc_data = encode_url_params(selected_params, apply_on_keys=cnst.DATEPICKER_FILTER_CONTROL_ID)
    url_params_dict = get_url_params(dash_br)
    assert_that(url_params_dict, equal_to(enc_data))
    # refresh the page
    dash_br.driver.refresh()
    # check url params still the same
    url_params_dict = get_url_params(dash_br)
    assert_that(url_params_dict, equal_to(enc_data))


def test_url_params_encoding_and_page_refresh_switch(dash_br):
    """Verifies that URL params for switch are correctly encoded and restored after a page refresh."""
    page_select(dash_br, page_name=cnst.SWITCH_CONTROL_PAGE)
    # switch 'Show active accounts' to True
    dash_br.multiple_click(switch_path_using_filter_control_id(filter_control_id=cnst.SWITCH_CONTROL_FALSE_ID), 1)
    # switch 'Show inactive accounts' to False
    dash_br.multiple_click(
        switch_path_using_filter_control_id(filter_control_id=cnst.SWITCH_CONTROL_TRUE_ID), 1, delay=0.1
    )
    # check correct urls params
    selected_params = {
        cnst.SWITCH_CONTROL_FALSE_ID: True,
        cnst.SWITCH_CONTROL_FALSE_DEFAULT_ID: False,
        cnst.SWITCH_CONTROL_TRUE_ID: False,
    }
    enc_data = encode_url_params(
        selected_params,
        apply_on_keys=[cnst.SWITCH_CONTROL_FALSE_ID, cnst.SWITCH_CONTROL_FALSE_DEFAULT_ID, cnst.SWITCH_CONTROL_TRUE_ID],
    )
    url_params_dict = get_url_params(dash_br)
    assert_that(url_params_dict, equal_to(enc_data))
    # refresh the page
    dash_br.driver.refresh()
    # check url params still the same
    url_params_dict = get_url_params(dash_br)
    assert_that(url_params_dict, equal_to(enc_data))
