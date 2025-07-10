from urllib.parse import parse_qs, urlencode, urlparse

import e2e.vizro.constants as cnst
import pytest
from e2e.asserts import decode_url_params, encode_url_params
from e2e.vizro.navigation import page_select
from hamcrest import assert_that, equal_to


def get_url_params(driver):
    current_url = driver.driver.current_url
    print("Current URL: ", current_url)
    # Parse URL
    parsed_url = urlparse(current_url)
    # Get query string and parse into dict
    params_dict = parse_qs(parsed_url.query)
    # Optional: convert single-value lists to actual values
    params_dict_simple = {k: v[0] if len(v) == 1 else v for k, v in params_dict.items()}
    print("Current URL params: ", params_dict_simple)
    return params_dict_simple


def param_to_url(decoded_map, apply_on_keys):
    print(
        "Param to url: ", urlencode(encode_url_params(decoded_map=decoded_map, apply_on_keys=apply_on_keys), doseq=True)
    )
    return urlencode(encode_url_params(decoded_map=decoded_map, apply_on_keys=apply_on_keys), doseq=True)


FILTERS_PAGE_APPLY_ON_KEYS = [cnst.DROPDOWN_FILTER_CONTROL_ID, cnst.RADIO_ITEMS_FILTER_CONTROL_ID]


def test_url_filters_encoding_and_page_refresh(dash_br):
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    # add steps with controls


    selected_params = {cnst.DROPDOWN_FILTER_CONTROL_ID: "virginica", cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "versicolor"}
    enc_data = encode_url_params(selected_params, apply_on_keys=FILTERS_PAGE_APPLY_ON_KEYS)
    params_dict_simple = get_url_params(dash_br)
    assert_that(params_dict_simple, equal_to(enc_data))
    dash_br.driver.refresh()
    params_dict_simple = get_url_params(dash_br)
    assert_that(params_dict_simple, equal_to(enc_data))


def test_url_filters_decoding_and_navigate_to_page(dash_br):
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    # add steps with controls
    selected_params = {cnst.DROPDOWN_FILTER_CONTROL_ID: "virginica", cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "versicolor"}
    params_dict_simple = get_url_params(dash_br)
    dec_data = decode_url_params(params_dict_simple, apply_on_keys=[cnst.DROPDOWN_FILTER_CONTROL_ID])
    assert_that(dec_data, equal_to(selected_params))
    page_select(dash_br, page_path=cnst.PARAMETERS_PAGE_PATH, page_name=cnst.PARAMETERS_PAGE)
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    dec_data = decode_url_params(params_dict_simple, apply_on_keys=[cnst.DROPDOWN_FILTER_CONTROL_ID])
    assert_that(dec_data, equal_to(selected_params))


@pytest.mark.parametrize(
    "dash_br_driver, expected_params",
    [
        (
            {
                "port": cnst.DEFAULT_PORT,
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{param_to_url(decoded_map={cnst.DROPDOWN_FILTER_CONTROL_ID: 'ALL'}, apply_on_keys=[cnst.DROPDOWN_FILTER_CONTROL_ID])}",
            },
            encode_url_params(
                decoded_map={
                    cnst.DROPDOWN_FILTER_CONTROL_ID: "ALL",
                    cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa"
                },
                apply_on_keys=FILTERS_PAGE_APPLY_ON_KEYS,
            ),
        ),
        (
            {
                "port": cnst.DEFAULT_PORT,
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{param_to_url(decoded_map={cnst.DROPDOWN_FILTER_CONTROL_ID: 'ALL', cnst.RADIO_ITEMS_FILTER_CONTROL_ID: 'versicolor'}, apply_on_keys=FILTERS_PAGE_APPLY_ON_KEYS)}",
            },
            encode_url_params(
                decoded_map={
                    cnst.DROPDOWN_FILTER_CONTROL_ID: "ALL",
                    cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "versicolor"
                },
                apply_on_keys=FILTERS_PAGE_APPLY_ON_KEYS),
        ),
        (
            {
                "port": cnst.DEFAULT_PORT,
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{param_to_url(decoded_map={cnst.DROPDOWN_FILTER_CONTROL_ID: 'setosa', cnst.RADIO_ITEMS_FILTER_CONTROL_ID: 'virginica'}, apply_on_keys=FILTERS_PAGE_APPLY_ON_KEYS)}",
            },
            encode_url_params(
                decoded_map={
                    cnst.DROPDOWN_FILTER_CONTROL_ID: 'setosa',
                    cnst.RADIO_ITEMS_FILTER_CONTROL_ID: 'virginica'
                },
                apply_on_keys=FILTERS_PAGE_APPLY_ON_KEYS
            ),
        ),
        (
            {
                "port": cnst.DEFAULT_PORT,
                "path": f"{cnst.FILTERS_PAGE_PATH}?{cnst.RADIO_ITEMS_FILTER_CONTROL_ID}=b64_InZlcnNpY29sb",
            },  # invalid value
            encode_url_params(
                decoded_map={
                    cnst.DROPDOWN_FILTER_CONTROL_ID: "ALL",
                    cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa"
                },
                apply_on_keys=FILTERS_PAGE_APPLY_ON_KEYS,
            ),
        ),
        (
            {
                "port": cnst.DEFAULT_PORT,
                "path": f"{cnst.FILTERS_PAGE_PATH}?"
                f"{cnst.DROPDOWN_FILTER_CONTROL_ID}=&{cnst.RADIO_ITEMS_FILTER_CONTROL_ID}=",
            },  # empty values
            encode_url_params(
                decoded_map={
                    cnst.DROPDOWN_FILTER_CONTROL_ID: "ALL",
                    cnst.RADIO_ITEMS_FILTER_CONTROL_ID: "setosa"
                },
                apply_on_keys=FILTERS_PAGE_APPLY_ON_KEYS,
            ),
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
                apply_on_keys=FILTERS_PAGE_APPLY_ON_KEYS,
            ),
        ),
    ],
    indirect=["dash_br_driver"],
)
def test_different_url_parameters(dash_br_driver, expected_params):
    print("\nEncoded expected data: ", expected_params)
    params_dict_simple = get_url_params(dash_br_driver)
    assert_that(params_dict_simple, equal_to(expected_params))
    # add controls checks
