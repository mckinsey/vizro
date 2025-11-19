from typing import Literal, Optional, Union

from dash import html, no_update
from pydantic import Field

from vizro.actions._abstract_action import _AbstractAction
from vizro.models._models_utils import _log_call
from vizro.models.types import _IdOrIdProperty

# Mapping of notification types to their corresponding colors and default icons (Google Material Icons)
VARIANT_CONFIG = {
    "info": {"className": "alert-info", "icon": "info"},
    "success": {"className": "alert-success", "icon": "check_circle"},
    "warning": {"className": "alert-warning", "icon": "warning"},
    "error": {"className": "alert-error", "icon": "error"},
}


class show_notification(_AbstractAction):
    """Shows a notification message using Dash Mantine Components notification system.

    This action displays notifications triggered by buttons, cards, figures, or other interactive components.
    Notifications support auto-dismissal, semantic variants, loading states, and dynamic updates.

    Args:
        title (Optional[str]): Notification title. Defaults to capitalized variant name if not provided.
        message (str): Main notification message text.
        variant (Literal["info", "success", "warning", "error"]): Semantic variant that determines color and
            default icon. Defaults to `"info"`.
        icon (Optional[str]): Icon name from [Google Material Icons](https://fonts.google.com/icons).
            Defaults to variant-specific icon. Ignored if `loading=True`.
        auto_close (Union[bool, int]): Auto-close duration in milliseconds. Set to `False` to disable.
            Defaults to `4000`.
        action (Literal["show", "update"]): Action type. `"show"` displays new notification, `"update"` modifies
            existing notification (requires matching `notification_id`). Defaults to `"show"`.
        notification_id (Optional[str]): Notification identifier for updates. Multiple actions can share the same
            `notification_id` to update a single notification.
        loading (bool): Show loading spinner instead of icon. Defaults to `False`.

    Example: Button triggering success notification
        ```python
        import vizro.actions as va
        import vizro.models as vm

        vm.Button(
            text="Save",
            actions=[
                va.show_notification(
                    message="Operation completed successfully!",
                    variant="success",
                    title="Success",
                )
            ],
        )
        ```
    """

    type: Literal["show_notification"] = "show_notification"
    title: Optional[str] = Field(
        default=None,
        description="Notification title. Defaults to capitalized variant name if not provided.",
    )
    message: str = Field(
        description="Main notification message text.",
    )
    # L: We could add another variant "plain" that doesn't have a default icon and color. Do you think that's usful?
    # For me it's fine, if it defaults to the info variant.
    variant: Literal["info", "success", "warning", "error"] = Field(
        default="info",
        description="Semantic variant that determines color and default icon.",
    )
    # L: We could remove icon if we don't want to expose too many arguments, but I do think it's useful to have.
    # Same for auto_close, action, and loading.
    icon: Optional[str] = Field(
        default=None,
        description="Icon name from Google Material Icons. Defaults to variant-specific icon. Ignored if loading=True.",
    )
    auto_close: Union[bool, int] = Field(
        default=4000,
        description="Auto-close duration in milliseconds. Set to False to disable.",
    )
    action: Literal["show", "update"] = Field(
        default="show",
        description="""Action type. `"show"` displays new notification, `"update"` modifies
            existing notification (requires matching `notification_id`).""",
    )
    # L: We need an extra field 'notification_id' to enable updating existing notifications.
    # Given that `id` can't be duplicated across the app, we use this field to update existing notifications.
    # See scratch dev app for an example. Or is there a way how I can just use `ìd` ? and the action
    # ids can be the same?
    notification_id: Optional[str] = Field(
        default=None,
        description="""Notification identifier for updates. Multiple actions can share the same
            `notification_id` to update a single notification.""",
    )
    loading: bool = Field(
        default=False,
        description="Show loading spinner instead of icon.",
    )
    # L: There is another argument called color that can be used to set the color of the notification.
    # but I didn't add it here, because I think the variant is more intuitive, though more restrictive.

    @property
    def outputs(self) -> list[_IdOrIdProperty]:  # type: ignore[override]
        return ["notification-container.sendNotifications"]

    @_log_call
    def function(self, _trigger):
        """Creates and returns a notification configuration for DMC NotificationContainer."""
        # L: Currently a notification is only shown if the action is triggered by a button or
        # other interactive component. So if the action is not triggered, we return no_update
        # to avoid showing a notification. However, do we think there will be use-cases where
        # we want to show a notification on page load?
        # On the other hand, we already have lots of arguments, so it might be too much.
        if not _trigger:
            return no_update

        # Get variant-specific configuration variables
        class_name = VARIANT_CONFIG[self.variant]["className"]
        icon_name = self.icon if self.icon else VARIANT_CONFIG[self.variant]["icon"]
        title = self.title if self.title else self.variant.capitalize()

        return [
            {
                "id": self.notification_id or self.id,
                "title": title,
                "message": self.message,
                "className": class_name,
                "icon": html.Span(icon_name, className="material-symbols-outlined"),
                "autoClose": self.auto_close,
                "action": self.action,
                "loading": self.loading,
            }
        ]
