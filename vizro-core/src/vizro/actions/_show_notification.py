from typing import Annotated, Literal, Optional, Union

from dash import html, no_update
from pydantic import AfterValidator, Field

from vizro.actions._abstract_action import _AbstractAction
from vizro.models._models_utils import _log_call, validate_icon
from vizro.models.types import _IdOrIdProperty

# Mapping of notification types to their corresponding colors and default icons (Google Material Icons)
VARIANT_CONFIG = {
    "info": {"className": "alert-info", "icon": "info"},
    "success": {"className": "alert-success", "icon": "check_circle"},
    "warning": {"className": "alert-warning", "icon": "warning"},
    "error": {"className": "alert-error", "icon": "error"},
    "progress": {"className": "alert-info", "icon": "info"},
}


class show_notification(_AbstractAction):
    """Shows a notification message using Dash Mantine Components notification system.

    This action displays notifications triggered by buttons, cards, figures, or other interactive components.
    Notifications support auto-dismissal, semantic variants, loading states, and dynamic updates.

    Args:
        title (Optional[str]): Notification title. Defaults to capitalized variant name if not provided.
        message (str): Main notification message text.
        variant (Literal["info", "success", "warning", "error", "progress"]): Semantic variant that determines color and
            default icon. Use `"progress"` to display a loading spinner instead of an icon. Defaults to "info".
        icon (str): Icon name from [Google Material Icons](https://fonts.google.com/icons).
            Defaults to variant-specific icon. Ignored if `variant="progress"`.
        auto_close (Union[bool, int]): Auto-close duration in milliseconds. Set to `False` to keep the notification
            open until the user closes it manually. Defaults to `4000`.
        notification_id (Optional[str]): Notification identifier for updates. Multiple actions can share the same 
            `notification_id` to update a single notification.
        action (Literal["show", "update"]): Action type. Use `"show"` to display a new notification or `"update"` 
            to modify an existing notification with matching `notification_id`. Defaults to `"show"`.

    Example: Button triggering notification
        ```python
        import vizro.actions as va
        import vizro.models as vm

        vm.Button(
            text="Save",
            actions=[
                va.show_notification(
                    message="Operation completed successfully!",
                    variant="success",
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
    variant: Literal["info", "success", "warning", "error", "progress"] = Field(
        default="info",
        description="""Semantic variant that determines color and default icon / loading state.
        If `progress`, the notification will show a loading spinner instead of an icon.""",
    )
    icon: Annotated[
        str,
        AfterValidator(validate_icon),
        Field(
            default="",
            description="""Icon name from Google Material icons library. Defaults to variant-specific icon.
                Ignored if `variant="progress"`""",
        ),
    ]
    auto_close: Union[bool, int] = Field(
        default=4000,
        description="""Auto-close duration in milliseconds. Set to `False` to keep the notification
            open until the user closes it manually. """,
    )
    notification_id: Optional[str] = Field(
        default="",
        description="""Notification identifier for updates. Multiple actions can share the same `notification_id` 
            to update a single notification.""",
    )
    # L: We do need this argument and can't make it depend on notification_id because both actions will have 
    # notification id provided. But one needs to have action 'update' and the other 'show'.
    action: Literal["show", "update"] = Field(
        default="show",
        description="""Action type. Use `"show"` to display a new notification or `"update"` to modify an existing 
            notification with matching `notification_id`.""",
    )

    @property
    def outputs(self) -> list[_IdOrIdProperty]:  # type: ignore[override]
        return ["notification-container.sendNotifications"]

    @_log_call
    def function(self, _trigger):
        """Creates and returns a notification configuration for DMC NotificationContainer."""
        if _trigger is None or _trigger == 0:
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
                "loading": self.variant == "progress",
            }
        ]
