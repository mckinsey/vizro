import e2e.vizro.constants as cnst
from e2e.vizro.navigation import page_select
from e2e.vizro.paths import button_id_path, page_title_path


def test_vizro_url(dash_br):
    """Verifies vizro_url component by opening datepicker page using vizro_url.href."""
    page_select(dash_br, page_name=cnst.VIZRO_URL_AND_DOWNLOAD_PAGE)
    dash_br.multiple_click(button_id_path(btn_id=cnst.BUTTON_VIZRO_URL), 1)
    dash_br.wait_for_text_to_equal(page_title_path(), text=cnst.DATEPICKER_PAGE)
