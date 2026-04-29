"""Clicking an example-questions menu item fills the textarea and activates send."""

from playwright.sync_api import Page, expect
from tests.integration.browser.conftest import SEND_ICON_FILLED, wait_for_send_icon


def test_clicking_example_question_fills_textarea_and_activates_send(page: Page, chat_app_url: str) -> None:
    page.goto(chat_app_url + "/example-questions")
    textarea = page.get_by_placeholder("Ask me anything or select an example...")
    expect(textarea).to_be_visible()

    page.locator("#example_chat-example-questions-button").click()
    first_item = page.get_by_role("menuitem").first
    expect(first_item).to_be_visible()
    item_text = first_item.inner_text().strip()

    first_item.click()

    expect(textarea).to_have_value(item_text)
    wait_for_send_icon(page, SEND_ICON_FILLED)
