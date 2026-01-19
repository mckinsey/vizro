import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm
from vizro import Vizro
from vizro.actions import show_notification, update_notification
from vizro.managers import model_manager


@pytest.fixture
def managers_one_page_one_button():
    vm.Page(
        id="page_one",
        title="Test Page",
        components=[vm.Button(id="button_one")],
    )
    Vizro._pre_build()


class TestShowNotificationInstantiation:
    def test_create_show_notification_mandatory_only(self):
        notification = show_notification(text="Test message")

        assert notification.type == "show_notification"
        assert notification.text == "Test message"
        assert notification.variant == "info"
        assert notification.title == "Info"
        assert notification.icon == "info"
        assert notification.auto_close == 4000
        assert notification.outputs == "vizro-notifications.sendNotifications"

    @pytest.mark.parametrize("field", ["title", "icon", "auto_close"])
    def test_none_value_raises_validation_error(self, field):
        with pytest.raises(ValidationError, match=field):
            show_notification(text="Test message", **{field: None})


@pytest.mark.usefixtures("managers_one_page_one_button")
class TestShowNotificationFunction:
    def test_function_default_notification(self):
        model_manager["button_one"].actions = [show_notification(id="test_notification", text="Info message")]
        action = model_manager["test_notification"]
        [result] = action.function()

        assert result["id"] == "test_notification"
        assert result["title"] == "Info"
        assert_component_equal(result["message"], dcc.Markdown(children="Info message", dangerously_allow_html=False))
        assert result["className"] == "alert-info"
        assert_component_equal(result["icon"], html.Span("info", className="material-symbols-outlined"))
        assert result["autoClose"] == 4000
        assert result["action"] == "show"
        assert result["loading"] is False

    def test_function_custom_notification(self):
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
        [result] = action.function()

        assert result["id"] == "custom_notification"
        assert result["title"] == "Custom Title"
        assert_component_equal(result["message"], dcc.Markdown(children="Test message", dangerously_allow_html=False))
        assert result["className"] == "alert-success"
        assert_component_equal(result["icon"], html.Span("star", className="material-symbols-outlined"))
        assert result["autoClose"] is False
        assert result["action"] == "show"
        assert result["loading"] is False

    @pytest.mark.parametrize(
        "variant,expected_class,expected_title,expected_icon,expected_loading,expected_auto_close",
        [
            ("info", "alert-info", "Info", "info", False, 4000),
            ("success", "alert-success", "Success", "check_circle", False, 4000),
            ("warning", "alert-warning", "Warning", "warning", False, 4000),
            ("error", "alert-error", "Error", "error", False, 4000),
            # The icon will just be ignored from dmc if loading is True.
            # Progress variant has auto_close=False by default
            ("progress", "alert-info", "Progress", "info", True, False),
        ],
    )
    def test_function_variants(
        self, variant, expected_class, expected_title, expected_icon, expected_loading, expected_auto_close
    ):
        model_manager["button_one"].actions = [show_notification(id="test_notification", text="test", variant=variant)]
        action = model_manager["test_notification"]
        [result] = action.function()

        assert result["title"] == expected_title
        assert result["className"] == expected_class
        assert_component_equal(result["icon"], html.Span(expected_icon, className="material-symbols-outlined"))
        assert result["loading"] == expected_loading
        assert result["autoClose"] == expected_auto_close


class TestUpdateNotificationInstantiation:
    def test_create_update_notification_mandatory_only(self):
        notification = update_notification(notification="test_notification", text="Updated message")

        assert notification.type == "update_notification"
        assert notification.notification == "test_notification"
        assert notification.text == "Updated message"
        assert notification.variant == "info"


@pytest.mark.usefixtures("managers_one_page_one_button")
class TestUpdateNotificationFunction:
    def test_function(self):
        show_action = show_notification(id="original_notification", text="Original message")
        update_action = update_notification(
            notification="original_notification",
            text="Updated message",
            title="Updated",
            variant="success",
        )
        model_manager["button_one"].actions = [show_action, update_action]
        [result] = update_action.function()

        assert result["id"] == "original_notification"
        assert result["title"] == "Updated"
        assert_component_equal(
            result["message"], dcc.Markdown(children="Updated message", dangerously_allow_html=False)
        )
        assert result["className"] == "alert-success"
        assert result["action"] == "update"
        assert result["loading"] is False


@pytest.mark.usefixtures("managers_one_page_one_button")
class TestUpdateNotificationPreBuild:
    def test_pre_build_notification_does_not_exist(self):
        invalid_update = update_notification(notification="nonexistent", text="Updated")
        with pytest.raises(ValueError, match="must refer to the ID of a `show_notification` action"):
            invalid_update.pre_build()
