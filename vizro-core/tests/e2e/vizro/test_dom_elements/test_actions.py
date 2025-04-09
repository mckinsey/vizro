import pytest
from e2e.asserts import assert_files_equal
from e2e.vizro import constants as cnst
from e2e.vizro.checkers import check_exported_file_exists
from e2e.vizro.navigation import page_select
from e2e.vizro.paths import button_path


def test_export_data_no_controls(dash_br):
    """Test exporting unfiltered data."""
    page_select(
        dash_br,
        page_path=cnst.EXPORT_PAGE_PATH,
        page_name=cnst.EXPORT_PAGE,
    )

    # download files and compare it with base ones
    dash_br.multiple_click(button_path(), 1)
    check_exported_file_exists(f"{dash_br.download_path}/{cnst.UNFILTERED_CSV}")
    check_exported_file_exists(f"{dash_br.download_path}/{cnst.UNFILTERED_XLSX}")
    assert_files_equal(cnst.UNFILTERED_BASE_CSV, f"{dash_br.download_path}/{cnst.UNFILTERED_CSV}")


def test_export_filtered_data(dash_br):
    """Test exporting filtered data. It is prefiltered in dashboard config."""
    page_select(
        dash_br,
        page_path=cnst.FILTERS_PAGE_PATH,
        page_name=cnst.FILTERS_PAGE,
    )

    # download files and compare it with base ones
    dash_br.multiple_click(button_path(), 1)
    check_exported_file_exists(f"{dash_br.download_path}/{cnst.FILTERED_CSV}")
    check_exported_file_exists(f"{dash_br.download_path}/{cnst.FILTERED_XLSX}")
    assert_files_equal(cnst.FILTERED_BASE_CSV, f"{dash_br.download_path}/{cnst.FILTERED_CSV}")


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_scatter_click_data_custom_action(dash_br):
    """Test custom action for changing data in card by interacting with graph."""
    page_select(
        dash_br,
        page_name=cnst.FILTER_INTERACTIONS_PAGE,
    )

    # click on the dot in the scatter graph and check card text values
    dash_br.click_at_coord_fractions(f"#{cnst.SCATTER_INTERACTIONS_ID} path:nth-of-type(20)", 0, 1)
    dash_br.wait_for_text_to_equal(f"#{cnst.CARD_INTERACTIONS_ID} p", "Scatter chart clicked data:")
    dash_br.wait_for_text_to_equal(f"#{cnst.CARD_INTERACTIONS_ID} h3", 'Species: "setosa"')
