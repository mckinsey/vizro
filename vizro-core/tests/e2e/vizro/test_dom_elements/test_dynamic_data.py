from pathlib import Path

import pytest
from e2e.asserts import assert_image_not_equal, assert_pixelmatch
from e2e.vizro import constants as cnst
from e2e.vizro.navigation import accordion_select, page_select, select_slider_handler
from e2e.vizro.waiters import callbacks_finish_waiter


@pytest.mark.parametrize(
    "cache, slider_id",
    [
        ("cached", cnst.SLIDER_DYNAMIC_DATA_CACHED_ID),
        ("cached_not", cnst.SLIDER_DYNAMIC_DATA_ID),
    ],
)
def test_data_dynamic_parametrization(dash_br, cache, slider_id):
    """This test checks parametrized data loading and how it is working with and without cache."""
    first_screen = f"{cache}_screen_first_test_data_dynamic_parametrization.png"
    second_screen = f"{cache}_screen_second_test_data_dynamic_parametrization.png"
    third_screen = f"{cache}_screen_third_test_data_dynamic_parametrization.png"
    accordion_select(
        dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION.upper(), accordion_number=cnst.DYNAMIC_DATA_ACCORDION_NUMBER
    )
    page_select(
        dash_br,
        page_path=cnst.DYNAMIC_DATA_PAGE_PATH,
        page_name=cnst.DYNAMIC_DATA_PAGE,
        graph_id=cnst.SCATTER_DYNAMIC_ID,
    )

    # move slider to value '20'
    select_slider_handler(dash_br, elem_id=slider_id, value=2)
    callbacks_finish_waiter(dash_br)
    dash_br.driver.save_screenshot(first_screen)

    # move slider to value '60'
    select_slider_handler(dash_br, elem_id=slider_id, value=6)
    callbacks_finish_waiter(dash_br)
    dash_br.driver.save_screenshot(second_screen)

    # move slider to value '20'
    select_slider_handler(dash_br, elem_id=slider_id, value=2)
    callbacks_finish_waiter(dash_br)
    dash_br.driver.save_screenshot(third_screen)

    # first and second screens should be different
    assert_image_not_equal(first_screen, second_screen)
    if cache == "cached":
        # first and third screens should be the same
        assert_pixelmatch(first_screen, third_screen)
    if cache == "not_cached":
        # first and third screens should be different
        assert_image_not_equal(first_screen, third_screen)
    for file in Path(".").glob("*test_data_dynamic_parametrization*"):
        file.unlink()
