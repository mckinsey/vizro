import e2e.vizro.constants as cnst
import pytest
from e2e.asserts import decode_url_params, encode_url_params, get_url_params, param_to_url
from e2e.vizro.checkers import check_selected_categorical_component, check_selected_dropdown
from e2e.vizro.navigation import clear_dropdown, page_select, select_dropdown_value
from e2e.vizro.paths import categorical_components_value_path, dropdown_arrow_path
from hamcrest import assert_that, equal_to


def test_url_filters_encoding_and_page_refresh(dash_br):
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    # select 'virginica' for dropdown and 'versicolor' for radio_items
    clear_dropdown(dash_br, dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE)
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE, value="virginica")
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.RADIO_ITEMS_FILTER_FILTERS_PAGE, value=2), 1, delay=0.1
    )
    selected_params = {cnst.DROPDOWN_FILTER_CONTROL_ID: ["virginica"], cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "versicolor"}
    # check correct urls params
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
    selected_params = {cnst.DROPDOWN_FILTER_CONTROL_ID: ["virginica"], cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "versicolor"}
    # check correct urls params
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
    "dash_br_driver, expected_params, radio_items_values_status, dropdown_selected_options, "
    "dropdown_unselected_options",
    [
        (
            {
                "port": cnst.DEFAULT_PORT,
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{param_to_url(decoded_map={cnst.DROPDOWN_FILTER_CONTROL_ID: ['setosa', 'versicolor', 'virginica']}, apply_on_keys=[cnst.DROPDOWN_FILTER_CONTROL_ID])}",  # noqa
            },
            encode_url_params(
                decoded_map={
                    cnst.DROPDOWN_FILTER_CONTROL_ID: ["setosa", "versicolor", "virginica"],
                    cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa",
                },
                apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS,
            ),
            [
                {"value": 1, "selected": True, "value_name": "setosa"},
                {"value": 2, "selected": False, "value_name": "versicolor"},
                {"value": 3, "selected": False, "value_name": "virginica"},
            ],
            ["setosa", "versicolor", "virginica"],
            [],
        ),
        (
            {
                "port": cnst.DEFAULT_PORT,
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{param_to_url(decoded_map={cnst.DROPDOWN_FILTER_CONTROL_ID: ['versicolor', 'virginica'], cnst.RADIO_ITEMS_FILTER_CONTROL_ID: 'versicolor'}, apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS)}",  # noqa
            },
            encode_url_params(
                decoded_map={
                    cnst.DROPDOWN_FILTER_CONTROL_ID: ["versicolor", "virginica"],
                    cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "versicolor",
                },
                apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS,
            ),
            [
                {"value": 1, "selected": False, "value_name": "setosa"},
                {"value": 2, "selected": True, "value_name": "versicolor"},
                {"value": 3, "selected": False, "value_name": "virginica"},
            ],
            ["versicolor", "virginica"],
            ["SelectAll", "setosa"],
        ),
        (
            {
                "port": cnst.DEFAULT_PORT,
                "path": f"{cnst.FILTERS_PAGE_PATH}?{cnst.RADIO_ITEMS_FILTER_CONTROL_ID}=b64_InZlcnNpY29sb",
            },  # invalid value
            encode_url_params(
                decoded_map={
                    cnst.DROPDOWN_FILTER_CONTROL_ID: ["setosa", "versicolor", "virginica"],
                    cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa",
                },
                apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS,
            ),
            [
                {"value": 1, "selected": True, "value_name": "setosa"},
                {"value": 2, "selected": False, "value_name": "versicolor"},
                {"value": 3, "selected": False, "value_name": "virginica"},
            ],
            ["setosa", "versicolor", "virginica"],
            [],
        ),
        (
            {
                "port": cnst.DEFAULT_PORT,
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{cnst.DROPDOWN_FILTER_CONTROL_ID}=&{cnst.RADIO_ITEMS_FILTER_CONTROL_ID}=",
            },  # empty values
            encode_url_params(
                decoded_map={
                    cnst.DROPDOWN_FILTER_CONTROL_ID: ["setosa", "versicolor", "virginica"],
                    cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa",
                },
                apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS,
            ),
            [
                {"value": 1, "selected": True, "value_name": "setosa"},
                {"value": 2, "selected": False, "value_name": "versicolor"},
                {"value": 3, "selected": False, "value_name": "virginica"},
            ],
            ["setosa", "versicolor", "virginica"],
            [],
        ),
        (
            {
                "port": cnst.DEFAULT_PORT,
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{cnst.DROPDOWN_FILTER_CONTROL_ID}=b64_WyJ2aXJnaW5pY2EiXQ&"  # ["virginica"]
                f"{cnst.RADIO_ITEMS_FILTER_CONTROL_ID}=InZpcmdpbmljYSI",
            },  # valid + invalid values
            encode_url_params(
                decoded_map={
                    cnst.DROPDOWN_FILTER_CONTROL_ID: ["virginica"],
                    cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa",
                },
                apply_on_keys=cnst.FILTERS_PAGE_APPLY_ON_KEYS,
            ),
            [
                {"value": 1, "selected": True, "value_name": "setosa"},
                {"value": 2, "selected": False, "value_name": "versicolor"},
                {"value": 3, "selected": False, "value_name": "virginica"},
            ],
            ["virginica"],
            ["SelectAll", "setosa", "versicolor"],
        ),
    ],
    indirect=["dash_br_driver"],
    ids=[
        "only dropdown value in url",
        "dropdown + radio_tems values in url",
        "invalid value",
        "empty values",
        "valid + invalid values",
    ],
)
def test_different_url_parameters(
    dash_br_driver, expected_params, radio_items_values_status, dropdown_selected_options, dropdown_unselected_options
):
    params_dict_simple = get_url_params(dash_br_driver)
    assert_that(params_dict_simple, equal_to(expected_params))
    # check that controls have correct values
    check_selected_categorical_component(
        dash_br_driver,
        component_id=cnst.RADIO_ITEMS_FILTER_FILTERS_PAGE,
        options_value_status=radio_items_values_status,
    )
    dash_br_driver.multiple_click(dropdown_arrow_path(cnst.DROPDOWN_FILTER_FILTERS_PAGE), 1)
    check_selected_dropdown(
        dash_br_driver,
        dropdown_id=cnst.DROPDOWN_FILTER_FILTERS_PAGE,
        expected_selected_options=dropdown_selected_options,
        expected_unselected_options=dropdown_unselected_options,
    )
