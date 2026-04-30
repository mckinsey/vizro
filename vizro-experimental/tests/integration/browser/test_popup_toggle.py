"""FAB click opens the popup panel; close button dismisses it."""

import re

from playwright.sync_api import Page, expect

_OPEN_CLASS = re.compile(r"\bchat-popup-panel-open\b")


def test_fab_click_opens_and_close_button_dismisses_panel(page: Page, popup_app_url: str) -> None:
    page.goto(popup_app_url + "/")

    panel = page.locator(".chat-popup-panel")
    expect(panel).to_be_attached()
    expect(panel).not_to_have_class(_OPEN_CLASS, timeout=5_000)

    page.locator("#chat_popup-toggle-button").click()
    expect(panel).to_have_class(_OPEN_CLASS, timeout=5_000)

    page.locator("#chat_popup-close-button").click()
    expect(panel).not_to_have_class(_OPEN_CLASS, timeout=5_000)
