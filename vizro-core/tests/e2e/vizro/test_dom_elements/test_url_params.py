import e2e.vizro.constants as cnst
import pytest
from e2e.asserts import decode_url_params, encode_url_params, get_url_params, param_to_url
from e2e.vizro.checkers import check_selected_categorical_component, check_selected_dropdown
from e2e.vizro.navigation import clear_dropdown, page_select, select_dropdown_value
from e2e.vizro.paths import categorical_components_value_path, dropdown_arrow_path, slider_value_path
from hamcrest import assert_that, equal_to


def test_url_filters_encoding_and_page_refresh(dash_br):
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
    "dash_br_driver, expected_decoded_map, selected_radio_items_values, dropdown_options",
    [
        (
            {
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{param_to_url(decoded_map={cnst.DROPDOWN_FILTER_CONTROL_ID: ['setosa', 'versicolor', 'virginica']}, apply_on_keys=[cnst.DROPDOWN_FILTER_CONTROL_ID])}",  # noqa
            },
            {
                cnst.DROPDOWN_FILTER_CONTROL_ID: ["setosa", "versicolor", "virginica"],
                cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa",
            },
            ["setosa"],
            [["setosa", "versicolor", "virginica"], []],
        ),
        (
            {
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{param_to_url(decoded_map={cnst.DROPDOWN_FILTER_CONTROL_ID: ['versicolor', 'virginica'], cnst.RADIO_ITEMS_FILTER_CONTROL_ID: 'versicolor'}, apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS)}",  # noqa
            },
            {
                cnst.DROPDOWN_FILTER_CONTROL_ID: ["versicolor", "virginica"],
                cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "versicolor",
            },
            ["versicolor"],
            [["versicolor", "virginica"], ["SelectAll", "setosa"]],
        ),
        (
            {
                "path": f"{cnst.FILTERS_PAGE_PATH}?{cnst.RADIO_ITEMS_FILTER_CONTROL_ID}=b64_InZlcnNpY29sb",
            },  # invalid value
            {
                cnst.DROPDOWN_FILTER_CONTROL_ID: ["setosa", "versicolor", "virginica"],
                cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa",
            },
            ["setosa"],
            [["setosa", "versicolor", "virginica"], []],
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
            ["setosa"],
            [["setosa", "versicolor", "virginica"], []],
        ),
        (
            {
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{cnst.DROPDOWN_FILTER_CONTROL_ID}=b64_WyJ2aXJnaW5pY2EiXQ&"  # ["virginica"]
                f"{cnst.RADIO_ITEMS_FILTER_CONTROL_ID}=InZpcmdpbmljYSI",
            },  # valid + invalid values
            {
                cnst.DROPDOWN_FILTER_CONTROL_ID: ["virginica"],
                cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa",
            },
            ["setosa"],
            [["virginica"], ["SelectAll", "setosa", "versicolor"]],
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
def test_different_url_parameters(dash_br_driver, expected_decoded_map, selected_radio_items_values, dropdown_options):
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
        expected_selected_options=dropdown_options[0],
        expected_unselected_options=dropdown_options[1],
    )


def test_url_params_encoding_and_page_refresh(dash_br):
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
