import pytest
from asserts import assert_component_equal
from dash import dcc, html

import vizro.models as vm
from vizro import Vizro
from vizro.actions import show_notification
from vizro.managers import model_manager


@pytest.fixture
def managers_one_page_one_button():
    """Instantiates a simple model_manager with a page and one button."""
    vm.Page(
        id="page_one",
        title="Test Page",
        components=[vm.Button(id="button_one")],
    )
    Vizro._pre_build()


class TestShowNotificationInstantiation:
    """Tests show_notification instantiation."""

    def test_create_show_notification_mandatory_only(self):
        notification = show_notification(message="Test message")

        assert notification.type == "show_notification"
        assert notification.message == "Test message"
        assert notification.variant == "info"
        assert notification.icon == ""
        assert notification.auto_close == 4000
        assert notification.action == "show"
        assert notification.notification_id == ""
        assert notification.outputs == ["notification-container.sendNotifications"]


@pytest.mark.usefixtures("managers_one_page_one_button")
class TestShowNotificationFunction:
    """Tests show_notification function behavior."""

    def test_button_triggered_default_notification(self):
        """Test notification triggered by button with default parameters."""
        model_manager["button_one"].actions = [show_notification(id="test_notification", message="Info message")]
        action = model_manager["test_notification"]
        result = action.function(_trigger=1)

        assert len(result) == 1
        assert result[0]["id"] == "test_notification"
        assert result[0]["title"] == "Info"
        assert_component_equal(
            result[0]["message"], dcc.Markdown(children="Info message", dangerously_allow_html=False)
        )
        assert result[0]["className"] == "alert-info"
        assert_component_equal(result[0]["icon"], html.Span("info", className="material-symbols-outlined"))
        assert result[0]["autoClose"] == 4000
        assert result[0]["action"] == "show"
        assert result[0]["loading"] is False

    def test_button_triggered_custom_notification(self):
        """Test notification with custom title, icon, and other parameters."""
        custom_notification = show_notification(
            id="custom_notification",
            title="Custom Title",
            message="Test message",
            variant="success",
            icon="star",
            auto_close=False,
            action="update",
            notification_id="custom_id",
        )

        model_manager["button_one"].actions = [custom_notification]
        action = model_manager["custom_notification"]
        result = action.function(_trigger=1)

        assert len(result) == 1
        assert result[0]["id"] == "custom_id"
        assert result[0]["title"] == "Custom Title"
        assert_component_equal(
            result[0]["message"], dcc.Markdown(children="Test message", dangerously_allow_html=False)
        )
        assert result[0]["className"] == "alert-success"
        assert_component_equal(result[0]["icon"], html.Span("star", className="material-symbols-outlined"))
        assert result[0]["autoClose"] is False
        assert result[0]["action"] == "update"
        assert result[0]["loading"] is False

    @pytest.mark.parametrize(
        "variant,expected_class,expected_icon,expected_loading,expected_auto_close",
        [
            ("info", "alert-info", "info", False, 4000),
            ("success", "alert-success", "check_circle", False, 4000),
            ("warning", "alert-warning", "warning", False, 4000),
            ("error", "alert-error", "error", False, 4000),
            # The icon will just be ignored from dmc if loading is True.
            # Progress variant has auto_close=False by default
            ("progress", "alert-info", "info", True, False),
        ],
    )
    def test_notification_variants(self, variant, expected_class, expected_icon, expected_loading, expected_auto_close):
        """Test all notification variants use correct defaults."""
        model_manager["button_one"].actions = [
            show_notification(id="test_notification", message=f"{variant} message", variant=variant)
        ]
        action = model_manager["test_notification"]
        result = action.function(_trigger=1)

        assert result[0]["title"] == variant.capitalize()
        assert result[0]["className"] == expected_class
        assert_component_equal(result[0]["icon"], html.Span(expected_icon, className="material-symbols-outlined"))
        assert result[0]["loading"] is expected_loading
        assert result[0]["autoClose"] == expected_auto_close
