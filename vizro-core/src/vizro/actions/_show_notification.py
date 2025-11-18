from typing import Literal, Optional, Union

from pydantic import Field

from vizro.actions._abstract_action import _AbstractAction
from vizro.models._models_utils import _log_call
from vizro.models.types import _IdOrIdProperty
from dash import html

# Mapping of notification types to their corresponding colors and default icons (Google Material Icons)
_NOTIFICATION_TYPE_CONFIG = {
    "info": {"color": "blue", "icon": "info"},
    "success": {"color": "green", "icon": "check_circle"},
    "warning": {"color": "yellow", "icon": "warning"},
    "error": {"color": "red", "icon": "error"},
}


class show_notification(_AbstractAction):
    """Shows a notification message using Dash Mantine Components notification system.

    This action displays a notification that can be triggered by buttons, cards, figures, or other interactive
    components. Notifications support auto-dismissal, semantic types (info, success, warning, error), and
    can show loading states or be updated dynamically.

    Args:
        message (str): Main notification message text.
        kind (Literal["info", "success", "warning", "error"]): Semantic kind of notification that
            determines color and default icon. Defaults to `"info"`.
        title (Optional[str]): Optional title for the notification. Defaults to `None`.
        icon (Union[str, bool, None]): Optional icon name from [Google Material Icons](https://fonts.google.com/icons)
            (e.g., "check_circle", "warning", "error", "notifications"). If not provided, a default icon based on the
            notification kind is used. Set to `False` to disable icon. Ignored if `loading=True`. Defaults to `None`.
        auto_close (Union[bool, int]): Duration in milliseconds before auto-closing. Set to `False` to disable
            auto-close. Defaults to `4000`.
        action (Literal["show", "update"]): Action to perform. `"show"` adds a new notification or queues it if
            limit is reached. `"update"` updates a previously shown notification (requires matching `notification_id`).
            Defaults to `"show"`.
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
                    kind="success",
                    title="Success",
                )
            ]
        )
        ```
    """

    type: Literal["show_notification"] = "show_notification"
    title: Optional[str] = Field(default=None, description="Optional title for the notification.")
    message: str = Field(description="Main notification message text.")
    kind: Literal["info", "success", "warning", "error"] = Field(
        default="info",
        description="Semantic kind of notification (info, success, warning, error).",
    )
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
    loading: bool = Field(
        default=False,
        description="Show loading spinner instead of icon.",
    )

    @property
    def outputs(self) -> list[_IdOrIdProperty]:  # type: ignore[override]
        return ["notification-container.sendNotifications"]

    @_log_call
    def function(self, _trigger):
        """Creates and returns a notification configuration for DMC NotificationContainer."""
        # Get the kind-specific config
        type_config = _NOTIFICATION_TYPE_CONFIG[self.kind]
        
        # Build the notification config dict
        notification = {
            "id": self.id,
            "action": self.action,
            "message": self.message,
            "color": type_config["color"],
            "autoClose": self.auto_close,
            "loading": self.loading,
        }
        
        if self.title:
            notification["title"] = self.title
        
        # Handle icon logic - only if not loading
        if not self.loading and self.icon is not False:
            icon_name = self.icon if self.icon else type_config["icon"]
            # Use Google Material icons (same as Vizro buttons)
            notification["icon"] = html.Span(
                icon_name,
                className="material-symbols-outlined",
            )
        
        # Return as a list as required by sendNotifications
        return [notification]
