from dataclasses import dataclass
from typing import Annotated, Literal

from dash import dcc, html
from pydantic import AfterValidator, Field

from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models._models_utils import _log_call, validate_icon
from vizro.models.types import ModelID, _IdOrIdProperty


@dataclass
class VariantDefaults:
    icon: str
    title: str
    className: str
    auto_close: bool | int = 4000


VARIANT_DEFAULTS: dict[str, VariantDefaults] = {
    "info": VariantDefaults(icon="info", title="Info", className="alert-info"),
    "success": VariantDefaults(icon="check_circle", title="Success", className="alert-success"),
    "warning": VariantDefaults(icon="warning", title="Warning", className="alert-warning"),
    "error": VariantDefaults(icon="error", title="Error", className="alert-error"),
    "progress": VariantDefaults(icon="info", title="Progress", className="alert-info", auto_close=False),
}


class show_notification(_AbstractAction):
    """Shows a notification message.

    Args:
        text (str): Markdown text for the main notification message. Follows the CommonMark specification.
        variant (Literal["info", "success", "warning", "error", "progress"]): Variant that determines color and
            default icon. If `progress`, the notification will show a loading spinner instead of an icon.
            Defaults to "info".
        title (str): Notification title. Defaults to capitalized variant name if not provided, for example
            'Info' for 'info' variant.
        icon (str): Icon name from the [Google Material Icon Library](https://fonts.google.com/icons). Defaults
            to the variant-specific icon, for example 'info' for 'info' variant. Ignored if `variant="progress"`.
        auto_close (bool | int): Auto-close duration in milliseconds. Set to `False` to keep the notification
            open until the user closes it manually. Default value depends on variant: `4000` for
            info/success/warning/error, `False` for progress.

    Example:
        ```python
        import vizro.actions as va
        import vizro.models as vm

        vm.Button(
            text="Save",
            actions=va.show_notification(
                title="Useful information",
                text="This is some useful information that you should know.",
            ),
        )
        ```
    """

    type: Literal["show_notification"] = "show_notification"

    text: str = Field(
        description="Markdown text for the main notification message. Follows the CommonMark specification.",
    )
    variant: Literal["info", "success", "warning", "error", "progress"] = Field(
        default="info",
        description="""Variant that determines color and default icon.
        If `progress`, the notification will show a loading spinner instead of an icon.""",
    )

    title: str = Field(
        default_factory=lambda data: VARIANT_DEFAULTS[data["variant"]].title,  # type: ignore[arg-type, misc]
        description="""Notification title. Defaults to capitalized variant name if not provided,
        for example 'Info' for 'info' variant.""",
    )
    icon: Annotated[
        str,
        AfterValidator(validate_icon),
        Field(
            default_factory=lambda data: VARIANT_DEFAULTS[data["variant"]].icon,
            description="""Icon name from Google Material icons library. Defaults to variant-specific icon.
                Ignored if `variant="progress"`""",
        ),
    ]
    auto_close: bool | int = Field(
        default_factory=lambda data: VARIANT_DEFAULTS[data["variant"]].auto_close,  # type: ignore[arg-type, misc]
        description="""Auto-close duration in milliseconds. Set to `False` to keep the notification
            open until the user closes it manually. Default value depends on variant: `4000` for
            info/success/warning/error, `False` for progress.""",
    )

    @property
    def outputs(self) -> _IdOrIdProperty:  # type: ignore[override]
        return "vizro_notifications.sendNotifications"

    @_log_call
    def function(self):
        notification = {
            "id": self.id,
            "title": self.title,
            "message": dcc.Markdown(children=self.text, dangerously_allow_html=False),
            "className": VARIANT_DEFAULTS[self.variant].className,
            "icon": html.Span(self.icon, className="material-symbols-outlined"),
            "autoClose": self.auto_close,
            "action": "show",
            "loading": self.variant == "progress",
        }
        return [notification]


class update_notification(show_notification):
    """Updates an existing notification message.

    This action updates notifications that were previously created with
    [`show_notification`][vizro.actions.show_notification]. `notification` must match the `id` of the original
    `show_notification` action.

    Args:
        notification (ModelID): Notification to update. Must match the id of the original `show_notification` action.
        text (str): Markdown text for the main notification message. Follows the CommonMark specification.
        variant (Literal["info", "success", "warning", "error", "progress"]): Variant that determines color and
            default icon. If `progress`, the notification will show a loading spinner instead of an icon.
            Defaults to "info".
        title (str): Notification title. Defaults to capitalized variant name if not provided, for example
            'Info' for 'info' variant.
        icon (str): Icon name from the [Google Material Icon Library](https://fonts.google.com/icons). Defaults
            to the variant-specific icon, for example 'info' for 'info' variant. Ignored if `variant="progress"`.
        auto_close (bool | int): Auto-close duration in milliseconds. Set to `False` to keep the notification
            open until the user closes it manually. Default value depends on variant: `4000` for
            info/success/warning/error, `False` for progress.

    Example:
        ```python
        import vizro.actions as va
        import vizro.models as vm

        vm.Button(
            text="Save",
            actions=[
                va.show_notification(id="save_notification", text="Saving data...", variant="progress"),
                va.export_data(),
                va.update_notification(
                    notification="save_notification", text="Data saved successfully!", variant="success"
                ),
            ],
        ```
        )"""

    type: Literal["update_notification"] = "update_notification"  # type: ignore[assignment]

    notification: ModelID = Field(
        description="Notification to update. Must match the id of the original `show_notification` action.",
    )

    @_log_call
    def pre_build(self):
        notification = model_manager[self.notification] if self.notification in model_manager else None

        # Use type rather than isinstance to rule out subclasses like update_notification itself.
        if type(notification) is not show_notification:
            raise ValueError(
                f"`notification={self.notification}` in `update_notification` action must refer to the ID of a "
                f"`show_notification` action."
            )

    @_log_call
    def function(self):
        [notification] = super().function()
        notification["id"] = self.notification
        notification["action"] = "update"
        return [notification]
