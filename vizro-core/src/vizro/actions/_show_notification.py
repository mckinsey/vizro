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

    This action displays a notification that can be triggered by buttons, cards, figures, or other interactive
    components. Notifications support auto-dismissal, semantic variants (info, success, warning, error), and
    can show loading states or be updated dynamically.

    Args:
        title (Optional[str]): Optional title for the notification. Defaults to `None`.
        message (str): Main notification message text.
        variant (Literal["info", "success", "warning", "error"]): Notification variant that
            determines default color and icon. Defaults to `"info"`.
        icon (Union[str, bool, None]): Optional icon name from [Google Material Icons](https://fonts.google.com/icons).
            If not provided, a default icon based on the variant is used. Set to `False` to disable icon.
            Ignored if `loading=True`. Defaults to `None`.
        auto_close (Union[bool, int]): Duration in milliseconds before auto-closing. Set to `False` to disable
            auto-close. Defaults to `4000`.
        action (Literal["show", "update"]): Action to perform. `"show"` adds a new notification or queues it if
            limit is reached. `"update"` updates a previously shown notification (requires matching `notification_id`).
            Defaults to `"show"`.
        notification_id (Optional[str]): ID for the notification in DMC. Used to update existing notifications with
            `action="update"`. Defaults to `None`.
        loading (bool): Show loading spinner instead of icon. Useful for operations in progress. Defaults to `False`.

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
    title: Optional[str] = Field(default=None, description="Optional title for the notification.")
    message: str = Field(description="Main notification message text.")
    # L: We could add another variant "plain" that doesn't have a default icon and color. Do you think that's usful?
    # For me it's fine, if it defaults to the info variant.
    variant: Literal["info", "success", "warning", "error"] = Field(
        default="info",
        description="Notification variant that determines default color and icon.",
    )
    # L: We could remove icon if we don't want to expose too many arguments, but I do think it's useful to have.
    # Same for auto_close, action, and loading.
    icon: Union[str, bool, None] = Field(
        default=None,
        description="Icon name from DashIconify, or False to disable icon. Uses type default if None.",
    )
    auto_close: Union[bool, int] = Field(
        default=4000,
        description="Duration in milliseconds before auto-closing. Set to False to disable auto-close.",
    )
    action: Literal["show", "update"] = Field(
        default="show",
        description="Action to perform: 'show' adds new notification, 'update' updates existing one.",
    )
    # L: We need an extra field 'notification_id' to enable updating existing notifications.
    # Given that `id` can't be duplicated across the app, we use this field to update existing notifications.
    # See scratch dev app for an example. Or is there a way how I can just use `ìd` ? and the action
    # ids can be the same?
    notification_id: Optional[str] = Field(
        default=None,
        description="""ID for the notification in DMC. Used to update existing notifications with action='update'.
        Defaults to the action's id.""",
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
        if not _trigger:
            return no_update

        # Get variant-specific configuration variables
        class_name = VARIANT_CONFIG[self.variant]["className"]
        icon_name = self.icon if self.icon else VARIANT_CONFIG[self.variant]["icon"]
        title = self.title if self.title else self.variant.capitalize()

        return [
            {
                "id": self.notification_id,
                "title": title,
                "message": self.message,
                "className": class_name,
                "icon": html.Span(icon_name, className="material-symbols-outlined"),
                "autoClose": self.auto_close,
                "action": self.action,
                "loading": self.loading,
            }
        ]
