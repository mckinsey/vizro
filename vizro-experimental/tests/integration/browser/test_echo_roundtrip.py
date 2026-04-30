"""Simple Echo round-trip: click send → user/assistant bubbles render, input resets."""

from playwright.sync_api import Page, expect
from tests.integration.browser.conftest import SEND_ICON_OUTLINED, wait_for_send_icon


def test_simple_echo_roundtrip(page: Page, chat_app_url: str) -> None:
    page.goto(chat_app_url + "/")
    textarea = page.get_by_placeholder("How can I help you?")
    expect(textarea).to_be_visible()

    textarea.fill("hello echo")
    page.locator("[id$='-send-button']").click()

    # The store also holds a hidden duplicate bubble tree, so scope to the visible container.
    rendered = page.locator("[id$='-rendered-messages']")
    expect(rendered.locator(".chat-message-bubble.chat-user-message")).to_have_text("hello echo")
    expect(rendered.locator(".chat-message-bubble.chat-assistant-message")).to_contain_text("You said: hello echo")

    expect(textarea).to_have_value("")
    wait_for_send_icon(page, SEND_ICON_OUTLINED)
