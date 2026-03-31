import time

import e2e.vizro.constants as cnst
import pytest
from e2e.vizro.navigation import accordion_select, page_select, select_slider_value
from e2e.vizro.paths import button_id_path


@pytest.mark.parametrize(
    "button_id, notification_id, expected_icon, expected_title, expected_message",
    [
        (
            cnst.SUCCESS_NOTIFICATION_BUTTON,
            cnst.SUCCESS_NOTIFICATION_ID,
            cnst.SUCCESS_NOTIFICATION_ICON,
            cnst.SUCCESS_NOTIFICATION_TITLE,
            cnst.SUCCESS_NOTIFICATION_MSG,
        ),
        (
            cnst.WARNING_NOTIFICATION_BUTTON,
            cnst.WARNING_NOTIFICATION_ID,
            cnst.WARNING_NOTIFICATION_ICON,
            cnst.WARNING_NOTIFICATION_TITLE,
            cnst.WARNING_NOTIFICATION_MSG,
        ),
        (
            cnst.ERROR_NOTIFICATION_BUTTON,
            cnst.ERROR_NOTIFICATION_ID,
            cnst.ERROR_NOTIFICATION_ICON,
            cnst.ERROR_NOTIFICATION_TITLE,
            cnst.ERROR_NOTIFICATION_MSG,
        ),
        (
            cnst.INFO_NOTIFICATION_BUTTON,
            cnst.INFO_NOTIFICATION_ID,
            cnst.INFO_NOTIFICATION_ICON,
            cnst.INFO_NOTIFICATION_TITLE,
            cnst.INFO_NOTIFICATION_MSG,
        ),
        (
            cnst.CUSTOM_NOTIFICATION_BUTTON,
            cnst.CUSTOM_NOTIFICATION_ID,
            cnst.CUSTOM_NOTIFICATION_ICON,
            cnst.CUSTOM_NOTIFICATION_TITLE,
            cnst.CUSTOM_NOTIFICATION_MSG,
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
    """Testing static notifications appearance and content."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.STATIC_NOTIFICATIONS_PAGE,
    )

    # Trigger notification and check its content
    dash_br.multiple_click(button_id_path(btn_id=button_id), 1)
    dash_br.wait_for_text_to_equal(f'#{notification_id} div[class$="Notification-icon"] span', expected_icon)
    dash_br.wait_for_text_to_equal(f'#{notification_id} div[class$="Notification-title"]', expected_title)
    dash_br.wait_for_text_to_equal(f'#{notification_id} div[class$="Notification-description"] p', expected_message)

    # Close notification
    dash_br.multiple_click(f'#{notification_id} button[class*="Notification-closeButton"]', 1)
    dash_br.wait_for_no_elements(f"#{notification_id}")


def test_progress_update_notification(dash_br):
    """Testing progress notification followed by update notification."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.STATIC_NOTIFICATIONS_PAGE,
    )

    # Trigger progress notification and check its content
    dash_br.multiple_click(button_id_path(btn_id=cnst.PROGRESS_NOTIFICATION_BUTTON), 1)
    dash_br.wait_for_element(f'#{cnst.UPDATE_NOTIFICATION_ID} span[class*="Notification-loader"]')
    dash_br.wait_for_text_to_equal(
        f'#{cnst.UPDATE_NOTIFICATION_ID} div[class$="Notification-title"]', cnst.PROGRESS_NOTIFICATION_TITLE
    )
    dash_br.wait_for_text_to_equal(
        f'#{cnst.UPDATE_NOTIFICATION_ID} div[class$="Notification-description"] p', cnst.PROGRESS_NOTIFICATION_MSG
    )

    # Simulate progress completion and check update notification content
    dash_br.multiple_click(button_id_path(btn_id=cnst.UPDATE_NOTIFICATION_BUTTON), 1)
    dash_br.wait_for_text_to_equal(
        f'#{cnst.UPDATE_NOTIFICATION_ID} div[class$="Notification-icon"] span', cnst.SUCCESS_NOTIFICATION_ICON
    )
    dash_br.wait_for_text_to_equal(
        f'#{cnst.UPDATE_NOTIFICATION_ID} div[class$="Notification-title"]', cnst.UPDATE_NOTIFICATION_TITLE
    )
    dash_br.wait_for_text_to_equal(
        f'#{cnst.UPDATE_NOTIFICATION_ID} div[class$="Notification-description"] p', cnst.UPDATE_NOTIFICATION_MSG
    )

    # Close update notification
    time.sleep(5)  # timeout for checking if notification does not auto close
    dash_br.multiple_click(f'#{cnst.UPDATE_NOTIFICATION_ID} button[class*="Notification-closeButton"]', 1)
    dash_br.wait_for_no_elements(f"#{cnst.UPDATE_NOTIFICATION_ID}")


def test_auto_close_notification(dash_br):
    """Testing auto-close notification."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.STATIC_NOTIFICATIONS_PAGE,
    )

    # Trigger auto-close notification and check its content
    dash_br.multiple_click(button_id_path(btn_id=cnst.AUTO_CLOSE_NOTIFICATION_BUTTON), 1)
    dash_br.wait_for_text_to_equal(
        f'#{cnst.AUTO_CLOSE_NOTIFICATION_ID} div[class$="Notification-icon"] span', cnst.INFO_NOTIFICATION_ICON
    )
    dash_br.wait_for_text_to_equal(
        f'#{cnst.AUTO_CLOSE_NOTIFICATION_ID} div[class$="Notification-title"]', cnst.AUTO_CLOSE_NOTIFICATION_TITLE
    )
    dash_br.wait_for_text_to_equal(
        f'#{cnst.AUTO_CLOSE_NOTIFICATION_ID} div[class$="Notification-description"] p',
        cnst.AUTO_CLOSE_NOTIFICATION_MSG,
    )

    # Wait for auto-close
    dash_br.wait_for_no_elements(f"#{cnst.AUTO_CLOSE_NOTIFICATION_ID}", timeout=10)


def test_notifications_limit(dash_br):
    """Testing that only a limited number of notifications (5) are shown at once."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.STATIC_NOTIFICATIONS_PAGE,
    )

    # Trigger multiple notifications
    dash_br.multiple_click(button_id_path(btn_id=cnst.SUCCESS_NOTIFICATION_BUTTON), 1)
    dash_br.multiple_click(button_id_path(btn_id=cnst.WARNING_NOTIFICATION_BUTTON), 1)
    dash_br.multiple_click(button_id_path(btn_id=cnst.ERROR_NOTIFICATION_BUTTON), 1)
    dash_br.multiple_click(button_id_path(btn_id=cnst.INFO_NOTIFICATION_BUTTON), 1)
    dash_br.multiple_click(button_id_path(btn_id=cnst.CUSTOM_NOTIFICATION_BUTTON), 1)
    dash_br.multiple_click(button_id_path(btn_id=cnst.PROGRESS_NOTIFICATION_BUTTON), 1)

    # timeout for checking if notification does not auto close
    time.sleep(5)

    # Check that only 5 notifications are shown
    dash_br.wait_for_no_elements(f"#{cnst.PROGRESS_NOTIFICATION_ID}")

    # Close one notification and check that the next one appears
    dash_br.multiple_click(f'#{cnst.SUCCESS_NOTIFICATION_ID} button[class*="Notification-closeButton"]', 1)
    dash_br.wait_for_element(f"#{cnst.PROGRESS_NOTIFICATION_ID}")

    # Trigger another notification and open a different page
    dash_br.multiple_click(button_id_path(btn_id=cnst.SUCCESS_NOTIFICATION_BUTTON), 1)
    page_select(dash_br, page_name=cnst.ACTION_CONTROL_SHORTCUT_PAGE)

    # timeout for checking if notification does not auto close
    time.sleep(5)

    # Check that no new notifications are shown on the new page
    dash_br.wait_for_no_elements(f"#{cnst.SUCCESS_NOTIFICATION_ID}")

    # Close one notification and check that the next one appears
    dash_br.multiple_click(f'#{cnst.WARNING_NOTIFICATION_ID} button[class*="Notification-closeButton"]', 1)
    dash_br.wait_for_element(f"#{cnst.SUCCESS_NOTIFICATION_ID}")


@pytest.mark.parametrize(
    "slider_value, button_id, expected_title, expected_message",
    [
        (
            1,
            cnst.CONDITIONAL_NOTIFICATION_ERROR_BUTTON_DEFAULT,
            cnst.ERROR_NOTIFICATION_TITLE,
            cnst.CONDITIONAL_NOTIFICATION_ERROR_MSG,
        ),
        (
            1,
            cnst.CONDITIONAL_NOTIFICATION_ERROR_BUTTON_NOTIFICATION_WITH_ERROR_MSG_AND_RESULT,
            cnst.ERROR_NOTIFICATION_TITLE,
            f"{cnst.CONDITIONAL_NOTIFICATION_CUSTOM_ERROR_MSG}{cnst.CONDITIONAL_NOTIFICATION_CUSTOM_ERROR_RESULT}",
        ),
        (
            2,
            cnst.CONDITIONAL_NOTIFICATION_SUCCESS_BUTTON,
            cnst.SUCCESS_NOTIFICATION_TITLE,
            cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG,
        ),
        (
            2,
            cnst.CONDITIONAL_NOTIFICATION_PROGRESS_BUTTON,
            cnst.PROGRESS_NOTIFICATION_TITLE,
            f"{cnst.CONDITIONAL_NOTIFICATION_PROGRESS_MSG}-2",
        ),
        (
            3,
            cnst.CONDITIONAL_NOTIFICATION_SUCCESS_BUTTON,
            cnst.SUCCESS_NOTIFICATION_TITLE,
            f"{cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG}{cnst.CONDITIONAL_NOTIFICATION_CUSTOM_SUCCESS_MSG}",
        ),
        (
            4,
            cnst.CONDITIONAL_NOTIFICATION_INFO_BUTTON,
            cnst.INFO_NOTIFICATION_TITLE,
            f"{cnst.CONDITIONAL_NOTIFICATION_INFO_MSG}{cnst.CONDITIONAL_NOTIFICATION_CUSTOM_INFO_MSG}",
        ),
        (
            5,
            cnst.CONDITIONAL_NOTIFICATION_WARNING_BUTTON,
            cnst.WARNING_NOTIFICATION_TITLE,
            f"{cnst.CONDITIONAL_NOTIFICATION_WARNING_MSG}{cnst.CONDITIONAL_NOTIFICATION_CUSTOM_WARNING_MSG}",
        ),
    ],
    ids=[
        "Error Notification",
        "Error Notification with custom message and result",
        "Success Notification default",
        "Progress Notification with dynamic message based on slider value",
        "Success Notification with custom message",
        "Info Notification with custom message",
        "Warning Notification with custom message",
    ],
)
def test_conditional_notifications(dash_br, slider_value, button_id, expected_title, expected_message):
    """Testing conditional notifications."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CONDITIONAL_NOTIFICATIONS_PAGE,
    )
    select_slider_value(dash_br, elem_id=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID, max_value=slider_value)

    # Trigger notification and check its content
    dash_br.multiple_click(button_id_path(btn_id=button_id), 1)
    dash_br.wait_for_text_to_equal('div[role="alert"] div[class$="Notification-title"]', expected_title)
    dash_br.wait_for_text_to_equal('div[role="alert"] div[class$="Notification-description"] p', expected_message)


def test_error_without_notification(dash_br):
    """Testing that error notification is not shown when notification for error is set to None."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CONDITIONAL_NOTIFICATIONS_PAGE,
    )
    select_slider_value(dash_br, elem_id=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID, max_value=1)

    # Trigger action that results in error and check that no notification is shown
    dash_br.multiple_click(button_id_path(btn_id=cnst.CONDITIONAL_NOTIFICATION_ERROR_BUTTON_NOTIFICATION_NONE), 1)
    dash_br.wait_for_no_elements('div[role="alert"]', timeout=1)


def test_three_success_notifications(dash_br):
    """Testing that three success notifications can be shown at once."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CONDITIONAL_NOTIFICATIONS_PAGE,
    )

    # Trigger three success notifications
    select_slider_value(dash_br, elem_id=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID, max_value=3)
    dash_br.multiple_click(button_id_path(btn_id=cnst.CONDITIONAL_NOTIFICATION_MULTIPLE_SUCCESS_BUTTON), 1)

    # Result of the first-in-chain `show_notification` action
    dash_br.wait_for_text_to_equal(
        'div[role="alert"]:nth-of-type(1) div[class$="Notification-description"] p',
        cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG_BEFORE_ACTION,
    )

    # Result of the second-in-chain conditional success notification
    dash_br.wait_for_text_to_equal(
        'div[role="alert"]:nth-of-type(2) div[class$="Notification-description"] p',
        cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG_INSIDE_ACTION,
    )

    # Result of the third-in-chain `show_notification` action
    dash_br.wait_for_text_to_equal(
        'div[role="alert"]:nth-of-type(3) div[class$="Notification-description"] p',
        cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG_AFTER_ACTION,
    )


def test_two_notifications_inside_one_action(dash_br):
    """Testing if two notifications are inside one action, the appropriate will be shown."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CONDITIONAL_NOTIFICATIONS_PAGE,
    )

    # Trigger action that has two notifications defined and check that the appropriate is shown
    select_slider_value(dash_br, elem_id=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID, max_value=4)
    dash_br.multiple_click(button_id_path(btn_id=cnst.CONDITIONAL_NOTIFICATION_IN_ONE_ACTION_BUTTON), 1)
    dash_br.wait_for_text_to_equal(
        'div[role="alert"] div[class$="Notification-description"] p',
        f"{cnst.CONDITIONAL_NOTIFICATION_INFO_MSG}{cnst.CONDITIONAL_NOTIFICATION_CUSTOM_INFO_MSG}",
    )


def test_progress_success_notification_chain(dash_br):
    """Testing that progress notification is updated with success content."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CONDITIONAL_NOTIFICATIONS_PAGE,
    )

    # Trigger action that results in progress notification followed by success notification and check their content
    for _ in range(2):
        dash_br.multiple_click(button_id_path(btn_id=cnst.CONDITIONAL_NOTIFICATION_PROGRESS_AND_SUCCESS_BUTTON), 1)
        dash_br.wait_for_text_to_equal(
            'div[role="alert"] div[class$="Notification-description"] p',
            cnst.CONDITIONAL_NOTIFICATION_PROGRESS_MSG,
        )
        dash_br.wait_for_text_to_equal(
            'div[role="alert"] div[class$="Notification-description"] p',
            cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG,
        )
        # Check that only one notification is shown
        dash_br.wait_for_no_elements('div[role="alert"]:nth-of-type(2)', timeout=1)


def test_notification_with_no_update_actions_chain(dash_br):
    """Testing that if all notifications are shown for action with no update actions chain."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CONDITIONAL_NOTIFICATIONS_PAGE,
    )

    # Trigger action that results in notification with no update actions chain and check its content
    dash_br.multiple_click(button_id_path(btn_id=cnst.CONDITIONAL_NOTIFICATION_MULTIPLE_NO_UPDATE_BUTTON), 1)

    # Check that two notifications are shown
    for alert_id in range(2):
        dash_br.wait_for_text_to_equal(
            f'div[role="alert"]:nth-of-type({alert_id}) div[class$="Notification-title"]',
            cnst.SUCCESS_NOTIFICATION_TITLE,
        )
        dash_br.wait_for_text_to_equal(
            f'div[role="alert"]:nth-of-type({alert_id}) div[class$="Notification-description"] p',
            f"Finished {alert_id} no_update action",
        )


@pytest.mark.parametrize(
    "button_id, expected_title, expected_message",
    [
        (
            cnst.CONDITIONAL_NOTIFICATION_MULTIPLE_PREVENT_UPDATE_BUTTON,
            # Note: PreventUpdate is treated as successfully finished action.
            cnst.SUCCESS_NOTIFICATION_TITLE,
            "Finished 1st no_update action",
        ),
        (
            cnst.CONDITIONAL_NOTIFICATION_MULTIPLE_VALUE_ERROR_BUTTON,
            cnst.ERROR_NOTIFICATION_TITLE,
            cnst.CONDITIONAL_NOTIFICATION_ERROR_MSG,
        ),
    ],
    ids=["Multiple PreventUpdate actions chain", "Multiple ValueError actions chain"],
)
def test_notification_with_prevent_update_value_error_actions_chain(
    dash_br, button_id, expected_title, expected_message
):
    """Testing that only first notification is processed for PreventUpdate and ValueError exceptions in the chain."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CONDITIONAL_NOTIFICATIONS_PAGE,
    )
    # Trigger action that results in notification with actions chain and check its content
    dash_br.multiple_click(button_id_path(btn_id=button_id), 1)

    # Check that proper notification are shown
    dash_br.wait_for_text_to_equal('div[role="alert"] div[class$="Notification-title"]', expected_title)
    dash_br.wait_for_text_to_equal('div[role="alert"] div[class$="Notification-description"] p', expected_message)

    # Check that only one notification is shown
    dash_br.wait_for_no_elements('div[role="alert"]:nth-of-type(2)', timeout=1)


@pytest.mark.xfail(reason="Waiting for implementation of showing notifications inside built-in actions")
def test_notifications_inside_builtin_action(dash_br):
    """Testing if notification inside built-in action is shown."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CONDITIONAL_NOTIFICATIONS_PAGE,
    )

    # Trigger action that results in notification inside built-in action and check its content
    select_slider_value(dash_br, elem_id=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID, max_value=5)
    dash_br.multiple_click(button_id_path(btn_id=cnst.CONDITIONAL_NOTIFICATION_EXPORT_BUTTON), 1)
    dash_br.wait_for_text_to_equal(
        f'#{cnst.CONDITIONAL_NOTIFICATION_PROGRESS_NOTIFICATION_ID} div[class$="Notification-description"]',
        cnst.CONDITIONAL_NOTIFICATION_PROGRESS_MSG,
    )
    dash_br.wait_for_text_to_equal(
        f'#{cnst.CONDITIONAL_NOTIFICATION_PROGRESS_NOTIFICATION_ID} div[class$="Notification-description"]',
        cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG,
    )
