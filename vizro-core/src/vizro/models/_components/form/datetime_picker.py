from contextlib import suppress
from datetime import date, datetime
from typing import Annotated, Any, Literal, cast

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html
from pydantic import AfterValidator, BeforeValidator, Field, JsonValue, PrivateAttr, model_validator
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

# Cache the underlying components' prop sets at import time so build() can split `extra` cheaply.
_DATE_PICKER_INPUT_PROPS = set(dmc.DatePickerInput().available_properties)
_TIME_PICKER_PROPS = set(dmc.TimePicker().available_properties)


def _validate_datetime_string_format(value: Any) -> Any:
    """Validate/normalize datetime values for the picker.

    ``datetime`` objects (including ``pandas.Timestamp``) are normalized to a seconds-precision ISO
    string, because ``dmc.TimePicker`` only renders ``HH:MM[:SS]`` — the sub-second precision of
    ``str(datetime)`` (e.g. ``"09:00:00.123456"``) breaks rendering and store round-trips.

    Strings are validated (not coerced) against the accepted shapes (in priority order):
      - ``YYYY-MM-DDTHH:MM:SS`` / ``YYYY-MM-DDTHH:MM``      (T separator)
      - ``YYYY-MM-DD HH:MM:SS`` / ``YYYY-MM-DD HH:MM``      (space separator, emitted by Mantine)
      - ``YYYY-MM-DD``                                       (date-only, time portion cleared)
    """

    def _validate(v: Any) -> Any:
        # datetime is a subclass of date, so this also catches pandas Timestamp. Drop sub-second
        # precision that dmc.TimePicker can't handle.
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%dT%H:%M:%S")
        if not (v and isinstance(v, str)):
            return v

        for fmt in (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        ):
            with suppress(ValueError):
                datetime.strptime(v, fmt)
                return v

        raise ValueError(
            f"Invalid datetime string {v!r}. Expected ISO format "
            "'YYYY-MM-DD', 'YYYY-MM-DDTHH:MM[:SS]', or 'YYYY-MM-DD HH:MM[:SS]'."
        )

    if isinstance(value, list):
        return [_validate(v) for v in value]
    return _validate(value)


def _split_iso_value(v: Any) -> tuple[str | None, str]:
    """Split a stored ISO date/datetime value into ``(date_part, time_part)`` for the sub-components.

    The time part is returned as ``""`` (not ``None``) when missing — ``dmc.TimePicker`` only clears
    when given an empty string; ``None`` is silently ignored, leaving stale displayed values.

    Returns ``(None, "")`` for falsey / non-string inputs. Returns ``(date, "")`` for date-only
    strings (time was cleared). Accepts both ``T`` and space separators.
    """
    if v is None or v == "":
        return None, ""
    s = str(v)
    if "T" in s:
        d, t = s.split("T", 1)
        return d, t
    if " " in s:
        d, t = s.split(" ", 1)
        return d, t
    return s, ""


class DateTimePicker(VizroBaseModel):
    """Temporal date-and-time-of-day single/range option selector.

    Can be provided to [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter].

    Under the hood this is rendered as a `dmc.DatePickerInput` plus one or two clearable
    `dmc.TimePicker` components, glued together by a clientside callback into a single
    proxy `dcc.Store` (`{id}.data`). When the time portion is cleared the store holds a
    date-only ISO string (`"YYYY-MM-DD"`), which the filter logic treats as start-of-day for
    the range start and end-of-day for the range end. Clearing the time therefore widens
    the filter to the whole day rather than disabling it.

    When used in a [dynamic filter](../user-guides/data.md#filters), the *date* portion is
    dynamic: `min` and `max` bound the date picker and refresh to the overall range found in
    the data on every reload, exactly like [`DatePicker`][vizro.models.DatePicker]. The time
    portion is always the full 00:00-23:59 day, so it has no dynamic bounds to update.

    Abstract: Usage documentation
        [How to use temporal selectors](../user-guides/selectors.md#temporal-selectors)

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
        # Accept strings as-is so input values stay in their original ISO format. Using only `datetime`
        # would coerce `"2026-03-01T08:00"` to `"2026-03-01T08:00:00"`, which would change the
        # minute-precision detection in the underlying filter coercion logic. We also accept pure
        # date strings (``"2026-03-01"``) which signal that the time portion is cleared.
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
                description="""Extra keyword arguments forwarded to the underlying `dmc.DatePickerInput`
and `dmc.TimePicker` components — each key is dispatched to whichever component accepts it.
Overrides Vizro defaults and may have unexpected behavior. See the dmc docs for available arguments:
https://www.dash-mantine-components.com/components/datepicker
https://www.dash-mantine-components.com/components/timepicker
[Not part of the official Vizro schema](../explanation/schema.md) and the underlying components may
change in the future.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)
    # DateTimePicker is composed of multiple inner components plus a proxy dcc.Store; there is no
    # single inner component whose properties should be auto-forwarded via Filter._selector_properties.
    _inner_component_properties: list[str] = PrivateAttr([])

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        # Both range and single modes expose their combined value through a proxy dcc.Store at `self.id`.
        return {"__default__": f"{self.id}.data"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}.data",
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.data"}

    @property
    def _dynamic_reload_hidden_ids(self) -> list[str]:
        """Component id(s) a dynamic `Filter` hides while reloading (see `Filter.build`).

        `self.id` is the non-visual proxy `dcc.Store`, so hide the wrapper holding the visible date/time
        inputs instead; the title sits outside the wrapper and stays visible during reload.
        """
        return [f"{self.id}_datetime_wrapper"]

    @staticmethod
    def _get_value_from_trigger(value: JsonValue, trigger: JsonValue) -> JsonValue:
        """Return the given `trigger` without modification."""
        return trigger

    def _split_extra(self) -> tuple[dict[str, Any], dict[str, Any]]:
        """Split ``self.extra`` into (date_picker_extra, time_picker_extra) by component prop set."""
        date_extra = {k: v for k, v in self.extra.items() if k in _DATE_PICKER_INPUT_PROPS}
        time_extra = {k: v for k, v in self.extra.items() if k in _TIME_PICKER_PROPS}
        return date_extra, time_extra

    def __call__(self, min, max):
        """Build the DateTimePicker component tree, bounding the date portion by ``min``/``max``.

        ``min``/``max`` bound the *date* portion only (the time portion is always the full 00:00-23:59
        day), so they are coerced to plain dates for the underlying ``dmc.DatePickerInput``. They accept
        ``date``/``datetime``/``pandas.Timestamp``/ISO string/``None``; a dynamic
        [`Filter`][vizro.models.Filter] passes ``pandas.Timestamp`` bounds computed from the reloaded
        data on every refresh.

        This does NOT register the clientside callbacks that glue the sub-components to the proxy
        ``dcc.Store`` — those are registered once in ``build`` (see the class docstring). Re-rendering the
        same-id sub-components re-binds them to that single registration, so a dynamic ``Filter`` can call
        this on every data reload without duplicating callback registration (which is why the date portion
        of the picker can be dynamic while the always-static time portion is unaffected).
        """
        # Coerce the bounds to plain dates: only the date sub-picker is bounded, and a runtime reload
        # supplies pandas.Timestamp values (carrying a time-of-day) which dmc would otherwise reject.
        min_date = _coerce_datetime_to_date(min)
        max_date = _coerce_datetime_to_date(max)

        description = self.description.build().children if self.description else [None]
        label_target_id = f"{self.id}-date-start" if self.range else f"{self.id}-date"
        label = (
            dbc.Label(
                children=[html.Span(id=f"{self.id}_title", children=self.title), *description],
                html_for=label_target_id,
            )
            if self.title
            else None
        )

        date_defaults: dict[str, Any] = {
            "minDate": min_date,
            "maxDate": max_date,
            "valueFormat": "MMM D, YYYY",
            "persistence": True,
            "persistence_type": "session",
            "withCellSpacing": False,
            "placeholder": "Pick a date",
        }
        time_defaults: dict[str, Any] = {
            "debounce": True,
            "persistence": True,
            "persistence_type": "session",
        }
        date_extra, time_extra = self._split_extra()

        if self.range:
            _value = cast(list[Any], [None, None] if self.value is None else self.value)
            start_date, start_time = _split_iso_value(_value[0])
            end_date, end_time = _split_iso_value(_value[1])

            return html.Div(
                children=[
                    label,
                    html.Div(
                        # A wrapper id so a dynamic Filter can grey out only the inputs during reload while
                        # keeping the title visible. selector.id is the proxy dcc.Store (no visual output).
                        id=f"{self.id}_datetime_wrapper",
                        children=[
                            html.Div(
                                children=[
                                    html.Div("From", className="vizro_datetime_picker_label"),
                                    html.Div(
                                        children=[
                                            dmc.DatePickerInput(
                                                id=f"{self.id}-date-start",
                                                type="default",
                                                value=start_date,
                                                **(date_defaults | date_extra),
                                            ),
                                            dmc.TimePicker(
                                                id=f"{self.id}-time-start",
                                                value=start_time,
                                                **(time_defaults | time_extra),
                                            ),
                                        ],
                                        className="vizro_datetime_picker_single",
                                    ),
                                ],
                                className="vizro_datetime_picker_range_item",
                            ),
                            html.Div(
                                children=[
                                    html.Div("To", className="vizro_datetime_picker_label"),
                                    html.Div(
                                        children=[
                                            dmc.DatePickerInput(
                                                id=f"{self.id}-date-end",
                                                type="default",
                                                value=end_date,
                                                **(date_defaults | date_extra),
                                            ),
                                            dmc.TimePicker(
                                                id=f"{self.id}-time-end",
                                                value=end_time,
                                                **(time_defaults | time_extra),
                                            ),
                                        ],
                                        className="vizro_datetime_picker_single",
                                    ),
                                ],
                                className="vizro_datetime_picker_range_item",
                            ),
                        ],
                        className="vizro_datetime_picker_range",
                    ),
                    dcc.Store(id=self.id, data=_value, storage_type="session"),
                ]
            )

        _value_single = cast(Any, self.value)
        date_part, time_part = _split_iso_value(_value_single)

        return html.Div(
            children=[
                label,
                html.Div(
                    # See the range branch: hide-target wrapper id, distinct from the proxy dcc.Store.
                    id=f"{self.id}_datetime_wrapper",
                    children=[
                        dmc.DatePickerInput(
                            id=f"{self.id}-date",
                            type="default",
                            value=date_part,
                            **(date_defaults | date_extra),
                        ),
                        dmc.TimePicker(
                            id=f"{self.id}-time",
                            value=time_part,
                            **(time_defaults | time_extra),
                        ),
                    ],
                    className="vizro_datetime_picker_single",
                ),
                dcc.Store(id=self.id, data=_value_single, storage_type="session"),
            ]
        )

    def _build_dynamic_placeholder(self, min, max):
        # Guarantee a value so the initial (pre-reload) placeholder renders the full available range.
        # Filter.pre_build already sets this via get_selector_default_value, so this is a defensive fallback
        # for a dynamic selector built outside that flow. Mirror get_selector_default_value exactly: date-only
        # ISO strings so the inline time shows as cleared, and empty strings when a bound is missing - never
        # the literal "None" (which f"{None}" would produce and which fails value validation).
        if not self.value:
            if self.range:
                self.value = [f"{min}", f"{max}"] if min is not None and max is not None else ["", ""]
            else:
                self.value = f"{min}" if min is not None else ""

        return self.__call__(min, max)

    @_log_call
    def build(self):
        # Register the clientside store-sync callback exactly once, at app startup. A dynamic Filter
        # re-renders this selector on every data reload through __call__ (never build), so the callback
        # must live here and not in __call__ — otherwise each reload would re-register it. The re-rendered
        # same-id sub-components re-bind to this single registration.
        if self.range:
            self._register_range_callback()
        else:
            self._register_single_callback()

        return (
            self._build_dynamic_placeholder(self.min, self.max) if self._dynamic else self.__call__(self.min, self.max)
        )

    def _register_range_callback(self):
        """Register the clientside callback that keeps the dcc.Store in sync with date+time inputs."""
        clientside_callback(
            ClientsideFunction(namespace="datetime_picker", function_name="update_range_datetime_picker_store"),
            output=[
                Output(self.id, "data"),
                Output(f"{self.id}-date-start", "value"),
                Output(f"{self.id}-date-end", "value"),
                Output(f"{self.id}-time-start", "value"),
                Output(f"{self.id}-time-end", "value"),
            ],
            inputs=[
                Input(self.id, "data"),
                Input(f"{self.id}-date-start", "value"),
                Input(f"{self.id}-date-end", "value"),
                Input(f"{self.id}-time-start", "value"),
                Input(f"{self.id}-time-end", "value"),
                State(self.id, "id"),
            ],
            hidden=True,
        )

    def _register_single_callback(self):
        """Register the clientside callback that keeps the dcc.Store in sync with the single date+time inputs."""
        clientside_callback(
            ClientsideFunction(namespace="datetime_picker", function_name="update_single_datetime_picker_store"),
            output=[
                Output(self.id, "data"),
                Output(f"{self.id}-date", "value"),
                Output(f"{self.id}-time", "value"),
            ],
            inputs=[
                Input(self.id, "data"),
                Input(f"{self.id}-date", "value"),
                Input(f"{self.id}-time", "value"),
                State(self.id, "id"),
            ],
            hidden=True,
        )
