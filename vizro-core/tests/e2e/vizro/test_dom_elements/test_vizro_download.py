import os

import e2e.vizro.constants as cnst
from e2e.asserts import assert_files_equal
from e2e.vizro.checkers import check_exported_file_exists
from e2e.vizro.navigation import page_select
from e2e.vizro.paths import button_id_path


def test_vizro_download_on_page_opening(dash_br):
    """Verifies that no data is downloaded if vizro_download component is present on the page."""
    page_select(dash_br, page_name=cnst.VIZRO_URL_AND_DOWNLOAD_PAGE)
    if not os.path.exists(f"{dash_br.download_path}/{cnst.VIZRO_DOWNLOAD_FILE}"):
        pass
    else:
        raise FileExistsError(f"{cnst.VIZRO_DOWNLOAD_FILE} exists")


def test_vizro_download(dash_br):
    """Verifies vizro_download component by downloading csv file using vizro_download.data."""
    page_select(dash_br, page_name=cnst.VIZRO_URL_AND_DOWNLOAD_PAGE)
    dash_br.multiple_click(button_id_path(btn_id=cnst.BUTTON_VIZRO_DOWNLOAD), 1)
    check_exported_file_exists(f"{dash_br.download_path}/{cnst.VIZRO_DOWNLOAD_FILE}")
    assert_files_equal(cnst.VIZRO_DOWNLOAD_BASE_FILE, f"{dash_br.download_path}/{cnst.VIZRO_DOWNLOAD_FILE}")
