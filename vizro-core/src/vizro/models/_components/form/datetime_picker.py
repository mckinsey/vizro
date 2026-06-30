from contextlib import suppress
from datetime import date, datetime
from typing import Annotated, Any, Literal, cast

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._components.form._form_utils import validate_date_time_range_picker, validate_max
from vizro.models._components.form.date_picker import _coerce_datetime_to_date
from vizro.models._models_utils import (
    _log_call,
    make_actions_chain,
    warn_description_without_title,
)
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionsType, _IdProperty


def _validate_datetime_string_format(value: Any) -> Any:
    """Validate string values parse as `YYYY-MM-DDTHH:MM` or `YYYY-MM-DDTHH:MM:SS` without coercing to datetime."""

    def _validate(v: Any) -> Any:
        if not (v and isinstance(v, str)):
            return v

        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
            with suppress(ValueError):
                datetime.strptime(v, fmt)
                return v

        raise ValueError(
            f"Invalid datetime string {v!r}. Expected ISO format 'YYYY-MM-DDTHH:MM' or 'YYYY-MM-DDTHH:MM:SS'."
        )

    if isinstance(value, list):
        return [_validate(v) for v in value]
    return _validate(value)


class DateTimePicker(VizroBaseModel):
    """Temporal date-and-time-of-day single/range option selector.

    Can be provided to [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter].

    Abstract: Usage documentation
        [How to use temporal selectors](user-guides/selectors.md#temporal-selectors)

    Example:
        ```python
        import pandas as pd
        import vizro.models as vm

        df = pd.DataFrame({"datetime_column": pd.to_datetime(["2026-01-01 09:00", "2026-06-15 14:30"])})

        vm.Filter(column="datetime_column", selector=vm.DateTimePicker())
        ```
    """

    type: Literal["datetime_picker"] = "datetime_picker"
    min: Annotated[date | None, BeforeValidator(_coerce_datetime_to_date)] = Field(
        default=None, description="Start date for the date portion of the datetime picker."
    )
    max: Annotated[
        date | None,
        BeforeValidator(_coerce_datetime_to_date),
        AfterValidator(validate_max),
        Field(default=None, description="End date for the date portion of the datetime picker."),
    ]
    value: Annotated[
        # Accept strings as-is so input values stay in their original ISO format. Using only `datetime` would coerce
        # `"2026-03-01T08:00"` to `"2026-03-01T08:00:00"`, which would change the minute-precision detection in
        # the underlying filter coercion logic.
        list[datetime | str] | datetime | str | None,
        AfterValidator(_validate_datetime_string_format),
        Field(default=None, description="Default datetime/datetimes for the datetime picker."),
    ]
    title: str = Field(default="", description="Title to be displayed.")
    range: Annotated[
        bool,
        AfterValidator(validate_date_time_range_picker),
        Field(default=True, description="Boolean flag for displaying range picker.", validate_default=True),
    ]
    # TODO: ideally description would have json_schema_input_type=str | Tooltip attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Tooltip | None,
        BeforeValidator(coerce_str_to_tooltip),
        AfterValidator(warn_description_without_title),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description.""",
        ),
    ]
    actions: ActionsType = []
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dmc.DateTimePicker` and overwrite
any defaults chosen by the Vizro team. This may have unexpected behavior.
Visit the [dmc documentation](https://www.dash-mantine-components.com/components/datetimepicker)
to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
underlying component may change in the future.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)
    _inner_component_properties: list[str] = PrivateAttr(dmc.DateTimePicker().available_properties)

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.{'data' if self.range else 'value'}"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}.{'data' if self.range else 'value'}",
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.{'data' if self.range else 'value'}"}

    @_log_call
    def build(self):
        description = self.description.build().children if self.description else [None]
        label = (
            dbc.Label(
                children=[html.Span(id=f"{self.id}_title", children=self.title), *description],
                html_for=f"{self.id}-start" if self.range else self.id,
            )
            if self.title
            else None
        )

        defaults: dict[str, Any] = {
            "debounce": True,
            "minDate": self.min,
            "maxDate": self.max,
            "valueFormat": "MMM D, YYYY HH:mm",
            "persistence": True,
            "persistence_type": "session",
        }
        if self.range:
            # Add the clientside callback only for range DateTimePicker
            self._update_range_datetime_picker_store()

            _value = cast(list[datetime | str | None], [None, None] if self.value is None else self.value)
            start_defaults = {"id": f"{self.id}-start", "value": _value[0], "label": "From", **defaults}
            # The end picker seeds its inner TimePicker with 23:59 so when the user picks only a date from the
            # calendar popover the time component fills as end-of-day rather than 00:00 (otherwise the end date
            # would silently exclude all rows on that day).
            end_defaults = {
                "id": f"{self.id}-end",
                "value": _value[1],
                "label": "To",
                "timePickerProps": {"defaultValue": "23:59:00"},
                **defaults,
            }

            return html.Div(
                children=[
                    label,
                    html.Div(
                        children=[
                            dmc.DateTimePicker(**(start_defaults | self.extra)),
                            dmc.DateTimePicker(**(end_defaults | self.extra)),
                        ],
                        style={"display": "flex", "gap": "8px"},
                    ),
                    dcc.Store(id=self.id, data=_value, storage_type="session"),
                ]
            )
        else:
            defaults = {"id": self.id, "value": self.value, **defaults}
            return html.Div(
                children=[
                    label,
                    dmc.DateTimePicker(**(defaults | self.extra)),
                ]
            )

    def _update_range_datetime_picker_store(self):
        """Define the clientside callback responsible for syncing the range datetime picker value with its store."""
        clientside_callback(
            ClientsideFunction(namespace="datetime_picker", function_name="update_range_datetime_picker_store"),
            output=[
                Output(self.id, "data"),
                Output(f"{self.id}-start", "value"),
                Output(f"{self.id}-end", "value"),
            ],
            inputs=[
                Input(self.id, "data"),
                Input(f"{self.id}-start", "value"),
                Input(f"{self.id}-end", "value"),
                State(self.id, "id"),
            ],
            hidden=True,
        )
