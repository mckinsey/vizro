"""Send-icon swaps outlined ↔ filled on input activity."""

from playwright.sync_api import Page, expect
from tests.integration.browser.conftest import SEND_ICON_FILLED, SEND_ICON_OUTLINED, wait_for_send_icon


def test_send_icon_toggles_with_input_value(page: Page, chat_app_url: str) -> None:
    page.goto(chat_app_url + "/")
    textarea = page.get_by_placeholder("How can I help you?")
    expect(textarea).to_be_visible()
    wait_for_send_icon(page, SEND_ICON_OUTLINED)

    textarea.fill("hello")
    wait_for_send_icon(page, SEND_ICON_FILLED)

    textarea.fill("")
    wait_for_send_icon(page, SEND_ICON_OUTLINED)
