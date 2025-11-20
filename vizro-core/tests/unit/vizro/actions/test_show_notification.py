import pytest
from asserts import assert_component_equal
from dash import html, no_update

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


@pytest.fixture
def managers_one_page_with_notification_action():
    """Instantiates a page with a notification action on page load."""
    vm.Page(
        id="page_two",
        title="Test Page",
        components=[vm.Card(text="Placeholder")],
        actions=[show_notification(id="page_notification", message="Page successfully loaded!")],
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
        assert notification.notification_id is None
        assert notification.loading is False
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
        assert result[0]["message"] == "Info message"
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
            loading=True,
        )

        model_manager["button_one"].actions = [custom_notification]
        action = model_manager["custom_notification"]
        result = action.function(_trigger=1)

        assert len(result) == 1
        assert result[0]["id"] == "custom_id"
        assert result[0]["title"] == "Custom Title"
        assert result[0]["message"] == "Test message"
        assert result[0]["className"] == "alert-success"
        assert_component_equal(result[0]["icon"], html.Span("star", className="material-symbols-outlined"))
        assert result[0]["autoClose"] is False
        assert result[0]["action"] == "update"
        assert result[0]["loading"] is True

    @pytest.mark.parametrize(
        "variant,expected_class,expected_icon",
        [
            ("info", "alert-info", "info"),
            ("success", "alert-success", "check_circle"),
            ("warning", "alert-warning", "warning"),
            ("error", "alert-error", "error"),
        ],
    )
    def test_notification_variants(self, variant, expected_class, expected_icon):
        """Test all notification variants use correct defaults."""
        model_manager["button_one"].actions = [
            show_notification(id="test_notification", message=f"{variant} message", variant=variant)
        ]
        action = model_manager["test_notification"]
        result = action.function(_trigger=1)

        assert result[0]["title"] == variant.capitalize()
        assert result[0]["className"] == expected_class
        assert_component_equal(result[0]["icon"], html.Span(expected_icon, className="material-symbols-outlined"))

    def test_button_not_triggered_returns_no_update(self):
        """Test that notification returns no_update when button is not triggered."""
        model_manager["button_one"].actions = [show_notification(id="test_notification", message="Test message")]
        action = model_manager["test_notification"]
        result_none = action.function(_trigger=None)
        result_zero = action.function(_trigger=0)

        assert result_none == no_update
        assert result_zero == no_update

    @pytest.mark.usefixtures("managers_one_page_with_notification_action")
    def test_page_action_on_load(self):
        """Test that page action shows notification on page load."""
        action = model_manager["page_notification"]
        result = action.function(_trigger=None)

        assert result != no_update
        assert result[0]["message"] == "Page successfully loaded!"
