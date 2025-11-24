import e2e.vizro.constants as cnst
import pytest
from e2e.vizro.navigation import accordion_select, page_select
from e2e.vizro.paths import button_id_path


@pytest.mark.parametrize(
    "button_id, notification_id, expected_icon, expected_title, expected_message",
    [
        (
            cnst.SUCCESS_NOTIFICATION_BUTTON,
            cnst.SUCCESS_NOTIFICATION_ID,
            cnst.SUCCESS_NOTIFICATION_ICON,
            cnst.SUCCESS_NOTIFICATION_TITLE,
            cnst.SUCCESS_NOTIFICATION_MESSAGE,
        ),
        (
            cnst.WARNING_NOTIFICATION_BUTTON,
            cnst.WARNING_NOTIFICATION_ID,
            cnst.WARNING_NOTIFICATION_ICON,
            cnst.WARNING_NOTIFICATION_TITLE,
            cnst.WARNING_NOTIFICATION_MESSAGE,
        ),
        (
            cnst.ERROR_NOTIFICATION_BUTTON,
            cnst.ERROR_NOTIFICATION_ID,
            cnst.ERROR_NOTIFICATION_ICON,
            cnst.ERROR_NOTIFICATION_TITLE,
            cnst.ERROR_NOTIFICATION_MESSAGE,
        ),
        (
            cnst.INFO_NOTIFICATION_BUTTON,
            cnst.INFO_NOTIFICATION_ID,
            cnst.INFO_NOTIFICATION_ICON,
            cnst.INFO_NOTIFICATION_TITLE,
            cnst.INFO_NOTIFICATION_MESSAGE,
        ),
        (
            cnst.CUSTOM_NOTIFICATION_BUTTON,
            cnst.CUSTOM_NOTIFICATION_ID,
            cnst.CUSTOM_NOTIFICATION_ICON,
            cnst.CUSTOM_NOTIFICATION_TITLE,
            cnst.CUSTOM_NOTIFICATION_MESSAGE,
        ),
    ],
    ids=[
        "Success Notification",
        "Warning Notification",
        "Error Notification",
        "Info Notification",
        "Custom Notification",
    ],
)
def test_notifications(dash_br, button_id, notification_id, expected_icon, expected_title, expected_message):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.STATIC_NOTIFICATIONS_PAGE,
    )

    dash_br.multiple_click(button_id_path(btn_id=button_id), 1)
    dash_br.wait_for_text_to_equal(f'#{notification_id} div[class$="Notification-icon"] span', expected_icon)
    dash_br.wait_for_text_to_equal(f'#{notification_id} div[class$="Notification-title"]', expected_title)
    dash_br.wait_for_text_to_equal(f'#{notification_id} div[class$="Notification-description"] p', expected_message)
    dash_br.multiple_click(f'#{notification_id} button[class*="Notification-closeButton"]', 1)
    dash_br.wait_for_no_elements(f"#{notification_id}")


def test_progress_update_notification(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.STATIC_NOTIFICATIONS_PAGE,
    )

    dash_br.multiple_click(button_id_path(btn_id=cnst.PROGRESS_NOTIFICATION_BUTTON), 1)
    dash_br.wait_for_element(f'#{cnst.UPDATE_NOTIFICATION_ID} span[class*="Notification-loader"]')
    dash_br.wait_for_text_to_equal(
        f'#{cnst.UPDATE_NOTIFICATION_ID} div[class$="Notification-title"]', cnst.PROGRESS_NOTIFICATION_TITLE
    )
    dash_br.wait_for_text_to_equal(
        f'#{cnst.UPDATE_NOTIFICATION_ID} div[class$="Notification-description"] p', cnst.PROGRESS_NOTIFICATION_MESSAGE
    )

    dash_br.multiple_click(button_id_path(btn_id=cnst.UPDATE_NOTIFICATION_BUTTON), 1)
    dash_br.wait_for_text_to_equal(
        f'#{cnst.UPDATE_NOTIFICATION_ID} div[class$="Notification-icon"] span', cnst.SUCCESS_NOTIFICATION_ICON
    )
    dash_br.wait_for_text_to_equal(
        f'#{cnst.UPDATE_NOTIFICATION_ID} div[class$="Notification-title"]', cnst.UPDATE_NOTIFICATION_TITLE
    )
    dash_br.wait_for_text_to_equal(
        f'#{cnst.UPDATE_NOTIFICATION_ID} div[class$="Notification-description"] p', cnst.UPDATE_NOTIFICATION_MESSAGE
    )
    dash_br.multiple_click(f'#{cnst.UPDATE_NOTIFICATION_ID} button[class*="Notification-closeButton"]', 1)
    dash_br.wait_for_no_elements(f"#{cnst.UPDATE_NOTIFICATION_ID}")


def test_auto_close_notification(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.STATIC_NOTIFICATIONS_PAGE,
    )

    dash_br.multiple_click(button_id_path(btn_id=cnst.AUTO_CLOSE_NOTIFICATION_BUTTON), 1)
    dash_br.wait_for_text_to_equal(
        f'#{cnst.AUTO_CLOSE_NOTIFICATION_ID} div[class$="Notification-icon"] span', cnst.INFO_NOTIFICATION_ICON
    )
    dash_br.wait_for_text_to_equal(
        f'#{cnst.AUTO_CLOSE_NOTIFICATION_ID} div[class$="Notification-title"]', cnst.AUTO_CLOSE_NOTIFICATION_TITLE
    )
    dash_br.wait_for_text_to_equal(
        f'#{cnst.AUTO_CLOSE_NOTIFICATION_ID} div[class$="Notification-description"] p',
        cnst.AUTO_CLOSE_NOTIFICATION_MESSAGE,
    )
    dash_br.wait_for_no_elements(f"#{cnst.AUTO_CLOSE_NOTIFICATION_ID}", timeout=10)
