from dataclasses import dataclass
from typing import Annotated, Literal

from dash import dcc, html
from pydantic import AfterValidator, Field, PrivateAttr, model_validator

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

    Abstract: Usage documentation
        [Notifications](../user-guides/notification-actions.md)

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
        description="Variant that determines color and default icon. "
        "If `progress`, the notification will show a loading spinner instead of an icon.",
    )

    # TODO: title, icon and auto_close could use default_factory once we bump to pydantic>=2.10.0.
    # For now, we use a model_validator with model_fields_set below to set variant-specific defaults.
    # Placeholder defaults are used to satisfy type checking; actual defaults are set in the validator.
    title: str = Field(
        default="",
        description='Notification title. Set to `""` to hide the title. '
        'Defaults to the capitalized variant name, for example `"Info"` for `variant="info"`.',
    )
    icon: Annotated[str, AfterValidator(validate_icon)] = Field(
        default="",
        description="Icon name from the [Google Material Icon Library](https://fonts.google.com/icons). "
        "Ignored if `variant='progress'`. Defaults to the variant-specific icon, for example 'info' for 'info' "
        "variant.",
    )
    auto_close: bool | int = Field(
        default=4000,
        description="Auto-close duration in milliseconds. Set to `False` to keep the notification "
        "open until the user closes it manually. Default value depends on variant: `4000` for "
        "info/success/warning/error, `False` for progress.",
    )

    _is_conditional: bool = PrivateAttr(False)

    # This should ideally be replaced with default_factory once we bump to pydantic>=2.10.0.
    @model_validator(mode="after")
    def set_variant_defaults(self):
        variant_defaults = VARIANT_DEFAULTS[self.variant]
        for field_name in ("title", "icon", "auto_close"):
            if field_name not in self.model_fields_set:
                self.__dict__[field_name] = getattr(variant_defaults, field_name)
        return self

    @property
    def outputs(self) -> _IdOrIdProperty:  # type: ignore[override]
        return "vizro-notifications.sendNotifications"

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

    @property
    def _dash_components(self) -> list[dcc.Download]:
        return [] if self._is_conditional else super()._dash_components

    def _define_callback(self):
        if not self._is_conditional:
            super()._define_callback()


class update_notification(show_notification):
    """Updates an existing notification message.

    This action updates notifications that were previously created with
    [`show_notification`][vizro.actions.show_notification]. `notification` must match the `id` of the original
    `show_notification` action.

    Abstract: Usage documentation
        [Update notification](../user-guides/notification-actions.md#update-existing-notification)

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
        )
        ```
    """

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
