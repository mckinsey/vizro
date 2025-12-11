import pytest
from asserts import assert_component_equal
from dash import dcc, html

import vizro.models as vm
from vizro import Vizro
from vizro.actions import show_notification, update_notification
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


class TestShowNotification:
    """Tests for show_notification action."""

    def test_instantiation_mandatory_only(self):
        """Test show_notification instantiation with only mandatory parameter."""
        notification = show_notification(text="Test message")

        assert notification.type == "show_notification"
        assert notification.text == "Test message"
        assert notification.variant == "info"
        assert notification.title == "Info"
        assert notification.icon == "info"
        assert notification.auto_close == 4000
        assert notification.outputs == "vizro_notifications.sendNotifications"

    @pytest.mark.usefixtures("managers_one_page_one_button")
    def test_function_default_notification(self):
        """Test notification triggered by button with default parameters."""
        model_manager["button_one"].actions = [show_notification(id="test_notification", text="Info message")]
        action = model_manager["test_notification"]
        result = action.function()

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

    @pytest.mark.usefixtures("managers_one_page_one_button")
    def test_function_custom_notification(self):
        """Test notification with custom title, icon, and other parameters."""
        custom_notification = show_notification(
            id="custom_notification",
            title="Custom Title",
            text="Test message",
            variant="success",
            icon="star",
            auto_close=False,
        )

        model_manager["button_one"].actions = [custom_notification]
        action = model_manager["custom_notification"]
        result = action.function()

        assert len(result) == 1
        assert result[0]["id"] == "custom_notification"
        assert result[0]["title"] == "Custom Title"
        assert_component_equal(
            result[0]["message"], dcc.Markdown(children="Test message", dangerously_allow_html=False)
        )
        assert result[0]["className"] == "alert-success"
        assert_component_equal(result[0]["icon"], html.Span("star", className="material-symbols-outlined"))
        assert result[0]["autoClose"] is False
        assert result[0]["action"] == "show"
        assert result[0]["loading"] is False

    @pytest.mark.usefixtures("managers_one_page_one_button")
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
    def test_function_variants(self, variant, expected_class, expected_icon, expected_loading, expected_auto_close):
        """Test all notification variants use correct defaults."""
        model_manager["button_one"].actions = [
            show_notification(id="test_notification", text=f"{variant} message", variant=variant)
        ]
        action = model_manager["test_notification"]
        result = action.function()

        assert result[0]["title"] == variant.capitalize()
        assert result[0]["className"] == expected_class
        assert_component_equal(result[0]["icon"], html.Span(expected_icon, className="material-symbols-outlined"))
        assert result[0]["loading"] == expected_loading
        assert result[0]["autoClose"] == expected_auto_close


class TestUpdateNotification:
    """Tests for update_notification action."""

    def test_instantiation(self):
        """Test update_notification instantiation."""
        notification = update_notification(notification="test_notification", text="Updated message")

        assert notification.type == "update_notification"
        assert notification.notification == "test_notification"
        assert notification.text == "Updated message"
        assert notification.variant == "info"

    @pytest.mark.usefixtures("managers_one_page_one_button")
    def test_function(self):
        """Test update_notification function updates existing notification."""
        # First create a show_notification
        show_action = show_notification(id="original_notification", text="Original message", variant="progress")
        model_manager["button_one"].actions = [show_action]

        # Then create an update_notification
        update_action = update_notification(
            notification="original_notification",
            text="Updated message",
            title="Updated",
            variant="success",
        )
        model_manager["button_one"].actions.append(update_action)

        result = update_action.function()

        assert len(result) == 1
        assert result[0]["id"] == "original_notification"
        assert result[0]["title"] == "Updated"
        assert_component_equal(
            result[0]["message"], dcc.Markdown(children="Updated message", dangerously_allow_html=False)
        )
        assert result[0]["className"] == "alert-success"
        assert result[0]["action"] == "update"
        assert result[0]["loading"] is False

    @pytest.mark.usefixtures("managers_one_page_one_button")
    def test_pre_build_validation(self):
        """Test update_notification validates that notification exists and is show_notification."""
        # Create a show_notification first
        show_action = show_notification(id="valid_notification", text="Test")
        model_manager["button_one"].actions = [show_action]

        # This should work
        update_action = update_notification(notification="valid_notification", text="Updated")
        update_action.pre_build()

        # This should fail - notification doesn't exist
        invalid_update = update_notification(notification="nonexistent", text="Updated")
        with pytest.raises(ValueError, match="must refer to the ID of a `show_notification` action"):
            invalid_update.pre_build()

        # This should fail - notification is not a show_notification (button_one is a Button, not show_notification)
        invalid_update2 = update_notification(notification="button_one", text="Updated")
        with pytest.raises(ValueError, match="must refer to the ID of a `show_notification` action"):
            invalid_update2.pre_build()
