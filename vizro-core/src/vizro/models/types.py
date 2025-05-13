"""Types used in pydantic fields."""

# ruff: noqa: F821
from __future__ import annotations

import functools
import importlib
import inspect
import sys
import warnings
from contextlib import contextmanager
from datetime import date
from typing import Annotated, Any, Literal, Optional, Protocol, Union, runtime_checkable

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

import plotly.io as pio
import pydantic_core as cs
from pydantic import (
    Discriminator,
    Field,
    StrictBool,
    Tag,
    ValidationInfo,
)
from pydantic.json_schema import SkipJsonSchema
from typing_extensions import TypedDict

from vizro.charts._charts_utils import _DashboardReadyFigure


def _get_layout_discriminator(layout: Any) -> Optional[str]:
    """Helper function for callable discriminator used for LayoutType."""
    # It is not immediately possible to introduce a discriminated union as a field type without it breaking existing
    # YAML/dictionary configuration in which `type` is not specified. This function is needed to handle the legacy case.
    if isinstance(layout, dict):
        # If type is supplied then use that (like saying discriminator="type"). Otherwise, it's the legacy case where
        # type is not specified, in which case we want to use vm.Layout, which has type="legacy_layout".
        try:
            return layout["type"]
        except KeyError:
            warnings.warn(
                "`layout` without an explicit `type` specified will no longer work in Vizro 0.2.0. To ensure "
                "future compatibility, specify `type: grid` for your `layout`.",
                FutureWarning,
                stacklevel=3,
            )
            return "legacy_layout"

    # If a model has been specified then this is equivalent to saying discriminator="type". When None is returned,
    # union_tag_not_found error is raised.
    return getattr(layout, "type", None)


def _get_action_discriminator(action: Any) -> Optional[str]:
    """Helper function for callable discriminator used for ActionType."""
    # It is not immediately possible to introduce a discriminated union as a field type without it breaking existing
    # YAML/dictionary configuration in which `type` is not specified. This function is needed to handle the legacy case.
    if isinstance(action, dict):
        # If type is supplied then use that (like saying discriminator="type"). Otherwise, it's the legacy case where
        # type is not specified, in which case we want to use vm.Action, which has type="action".
        try:
            # TODO-AV2 C 1: Put in deprecation warning.
            return action["type"]
        except KeyError:
            return "action"

    # If a model has been specified then this is equivalent to saying discriminator="type". When None is returned,
    # union_tag_not_found error is raised.
    return getattr(action, "type", None)


def _clean_module_string(module_string: str) -> str:
    from vizro.models._models_utils import REPLACEMENT_STRINGS

    for original, new in REPLACEMENT_STRINGS.items():
        if original in module_string:
            return new
    return ""


# Used to describe _DashboardReadyFigure, so we can keep CapturedCallable generic rather than referring to
# _DashboardReadyFigure explicitly.
@runtime_checkable
class _SupportsCapturedCallable(Protocol):
    _captured_callable: CapturedCallable


class JsonSchemaExtraType(TypedDict):
    """Type that specifies the extra information needed to parse a CapturedCallable from JSON/YAML."""

    import_path: str
    mode: str


def validate_captured_callable(cls, value, info: ValidationInfo):
    """Reusable validator for the `figure` argument of Figure like models."""
    # Bypass validation so that legacy vm.Action(function=filter_interaction(...)) and
    # vm.Action(function=export_data(...)) work.
    from vizro.actions import export_data, filter_interaction

    if isinstance(value, (export_data, filter_interaction)):
        return value

    # TODO[MS]: We may want to double check on the mechanism of how field info is brought to. This seems
    # to get deprecated in V3
    json_schema_extra: JsonSchemaExtraType = cls.model_fields[info.field_name].json_schema_extra
    return CapturedCallable._validate_captured_callable(
        captured_callable_config=value, json_schema_extra=json_schema_extra
    )


class CapturedCallable:
    """Stores a captured function call to use in a dashboard.

    Users do not need to instantiate this class directly. Instances are instead generated automatically
    through the [`capture`][vizro.models.types.capture] decorator. Some of the functionality is similar to
    `functools.partial`.

    Ready-to-use `CapturedCallable` instances are provided by Vizro. In this case refer to the [user guide on
    Charts/Graph](../user-guides/graph.md), [Table](../user-guides/table.md), [Actions](../user-guides/actions.md)
    or [Figures](../user-guides/figure.md) to see available choices.

    (Advanced) In case you would like to create your own `CapturedCallable`, please refer to the [user guide on
    custom charts](../user-guides/custom-charts.md),
    [custom tables](../user-guides/custom-tables.md),
    [custom actions](../user-guides/custom-actions.md),
    or [custom figures](../user-guides/custom-figures.md).
    """

    def __init__(self, function, /, *args, **kwargs):
        """Creates a new `CapturedCallable` object that will be able to re-run `function`.

        Partially binds *args and **kwargs to the function call.

        Raises:
            ValueError if `function` contains positional-only or variadic positional parameters (*args).

        """
        # It is difficult to get positional-only and variadic positional arguments working at the same time as
        # variadic keyword arguments. Ideally we would do the __call__ as
        # self.__function(*bound_arguments.args, **bound_arguments.kwargs) as in the
        # Python documentation. This would handle positional-only and variadic positional arguments better but makes
        # it more difficult to handle variadic keyword arguments due to https://bugs.python.org/issue41745.
        # Hence we abandon bound_arguments.args and bound_arguments.kwargs in favor of just using
        # self.__function(**bound_arguments.arguments).
        parameters = inspect.signature(function).parameters
        invalid_params = {
            param.name
            for param in parameters.values()
            if param.kind in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.VAR_POSITIONAL]
        }

        if invalid_params:
            raise ValueError(
                f"Invalid parameter {', '.join(invalid_params)}. CapturedCallable does not accept functions with "
                f"positional-only or variadic positional parameters (*args)."
            )

        self.__function = function
        self.__bound_arguments = inspect.signature(function).bind_partial(*args, **kwargs).arguments
        self.__unbound_arguments = [
            param for param in parameters.values() if param.name not in self.__bound_arguments
        ]  # Maintaining the same order here is important.

        # A function can only ever have one variadic keyword parameter. {""} is just here so that var_keyword_param
        # is always unpacking a one element set.
        (var_keyword_param,) = {
            param.name for param in parameters.values() if param.kind == inspect.Parameter.VAR_KEYWORD
        } or {""}

        # Since we do __call__ as self.__function(**bound_arguments.arguments), we need to restructure the arguments
        # a bit to put the kwargs in the right place.
        # For a function with parameter **kwargs this converts self.__bound_arguments = {"kwargs": {"a": 1}} into
        # self.__bound_arguments = {"a": 1}.
        if var_keyword_param in self.__bound_arguments:
            self.__bound_arguments.update(self.__bound_arguments[var_keyword_param])
            del self.__bound_arguments[var_keyword_param]

        # Used in later validations of the captured callable.
        self._mode = None
        self._model_example = None

    def __call__(self, *args, **kwargs):
        """Run the `function` with the initially bound arguments overridden by `**kwargs`.

        *args are possible here, but cannot be used to override arguments bound in `__init__` - just to
        provide additional arguments. You can still override arguments that were originally given
        as positional using their argument name.
        """
        if args and kwargs:
            # In theory we could probably lift this restriction, but currently we don't need to and we'd need
            # to give careful thought on the right way to handle cases where there's ambiguity in the
            # self.__function call as the same argument is potentially being provided through both *args and **kwargs.
            raise ValueError("CapturedCallable does not support calling with both positional and keyword arguments.")

        # In order to avoid any ambiguity in the call to self.__function, we cannot provide use the *args directly.
        # Instead they must converted to keyword arguments and so we need to match them up with the right keywords.
        # Since positional-only or variadic positional parameters are not possible (they raise ValueError in __init__)
        # the only possible type of argument *args could be address is positional-or-keyword.
        if args:
            unbound_positional_arguments = [
                param.name
                for param in self.__unbound_arguments
                if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            ]
            if len(args) > len(unbound_positional_arguments):
                # TypeError to match the standard Python exception raised in this case.
                raise TypeError(
                    f"CapturedCallable takes {len(unbound_positional_arguments)} "
                    f"positional arguments but {len(args)} were given."
                )

            # No need to handle case that len(args) < len(unbound_positional_arguments),
            # since this will already raise error in the following function call.
            return self.__function(**dict(zip(unbound_positional_arguments, args)), **self.__bound_arguments)

        return self.__function(**{**self.__bound_arguments, **kwargs})

    def __getitem__(self, arg_name: str):
        """Gets the value of a bound argument."""
        return self.__bound_arguments[arg_name]

    def __setitem__(self, arg_name: str, value):
        """Sets the value of a bound argument."""
        self.__bound_arguments[arg_name] = value

    @property
    def _arguments(self):
        # TODO: This is used twice: in _get_parametrized_config and in vm.Action and should be removed when those
        # references are removed.
        # TODO-AV2 B 1: try to subclass Mapping. Check if anything requires MutableMapping (used in Vizro AI tests
        #  and to set data_frame only?). Try to remove these by making special method for setting data_frame. Then
        # can remove as many uses of _arguments as possible and use .items() where suitable instead.
        return self.__bound_arguments

    @property
    def _function(self):
        # TODO-AV2 B 2: see if this can be removed.
        return self.__function

    @classmethod
    def _validate_captured_callable(
        cls,
        captured_callable_config: Union[dict[str, Any], _SupportsCapturedCallable, CapturedCallable],
        json_schema_extra: JsonSchemaExtraType,
    ):
        value = cls._parse_json(captured_callable_config=captured_callable_config, json_schema_extra=json_schema_extra)
        value = cls._extract_from_attribute(value)
        value = cls._check_type(captured_callable=value, json_schema_extra=json_schema_extra)
        return value

    # TODO: The below could be transferred to a custom type similar to this example:
    # https://docs.pydantic.dev/2.9/concepts/types/#handling-third-party-types
    # TODO: Ultimately we are calling this, but it is always true, as the before validator catches things anyway
    # In future: we should really get rid of this and make a custom type annotation that does the job of validation
    # and schema generation.
    # Once we have a custom schema for captured callables, we can bypass the core schema and return a custom schema.
    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: Any) -> cs.core_schema.CoreSchema:
        """Core validation, which boils down to checking if it is a custom type."""
        return cs.core_schema.no_info_plain_validator_function(cls.core_validation)

    @staticmethod
    def core_validation(value: Any):
        """Core validation logic."""
        if not isinstance(value, CapturedCallable):
            raise ValueError(f"Expected CapturedCallable, got {type(value)}")
        return value

    @classmethod
    def _parse_json(
        cls,
        captured_callable_config: Union[_SupportsCapturedCallable, CapturedCallable, dict[str, Any]],
        json_schema_extra: JsonSchemaExtraType,
    ) -> Union[CapturedCallable, _SupportsCapturedCallable]:
        """Parses captured_callable_config specification from JSON/YAML.

        If captured_callable_config is already _SupportCapturedCallable or CapturedCallable then it just passes through
        untouched.

        This uses the hydra syntax for _target_ but none of the other bits and we don't actually use hydra
        to implement it. In future, we might like to switch to using hydra's actual implementation
        which would allow nested functions (e.g. for transformers?) and to specify the path to a _target_ that lives
        outside of vizro.plotly_express. See https://hydra.cc/docs/advanced/instantiate_objects/overview/.
        """
        if not isinstance(captured_callable_config, dict):
            return captured_callable_config

        # Try to import function given in _target_ from the import_path property of the pydantic field.
        try:
            function_name = captured_callable_config.pop("_target_")
        except KeyError as exc:
            raise ValueError(
                "CapturedCallable object must contain the key '_target_' that gives the target function."
            ) from exc

        import_path = json_schema_extra["import_path"]
        try:
            function = getattr(importlib.import_module(import_path), function_name)
        except (AttributeError, ModuleNotFoundError) as exc:
            raise ValueError(f"_target_={function_name} cannot be imported from {import_path}.") from exc

        # All the other items in figure are the keyword arguments to pass into function.
        function_kwargs = captured_callable_config

        # It would seem natural to return cls(function, **function_kwargs) here, but the function is already decorated
        # with @capture, and so that would return a nested CapturedCallable.
        return function(**function_kwargs)

    @classmethod
    def _extract_from_attribute(
        cls, captured_callable: Union[_SupportsCapturedCallable, CapturedCallable]
    ) -> CapturedCallable:
        """Extracts CapturedCallable from _SupportCapturedCallable (e.g. _DashboardReadyFigure).

        If captured_callable is already CapturedCallable then it just passes through untouched.
        """
        if not isinstance(captured_callable, _SupportsCapturedCallable):
            return captured_callable
        return captured_callable._captured_callable

    @classmethod
    def _check_type(
        cls, captured_callable: CapturedCallable, json_schema_extra: JsonSchemaExtraType
    ) -> CapturedCallable:
        """Checks captured_callable is right type and mode."""
        from vizro.actions import export_data, filter_interaction

        # Bypass validation so that legacy {"function": {"_target_": "filter_interaction"}} and
        # {"function": {"_target_": "export_data"}} work.
        if isinstance(captured_callable, (export_data, filter_interaction)):
            return captured_callable

        expected_mode = json_schema_extra["mode"]
        import_path = json_schema_extra["import_path"]

        if not isinstance(captured_callable, CapturedCallable):
            raise ValueError(
                f"Invalid CapturedCallable. Supply a function imported from {import_path} or defined with "
                f"decorator @capture('{expected_mode}')."
            )

        if (mode := captured_callable._mode) != expected_mode:
            raise ValueError(
                f"CapturedCallable was defined with @capture('{mode}') rather than @capture('{expected_mode}') and so "
                "is not compatible with the model."
            )

        return captured_callable

    def __repr__(self):
        """String representation of the CapturedCallable."""
        args = ", ".join(f"{key}={value!r}" for key, value in self._arguments.items())
        return f"{self._function.__module__}.{self._function.__name__}({args})"

    def __repr_clean__(self):
        """Alternative __repr__ method with cleaned module paths."""
        args = ", ".join(f"{key}={value!r}" for key, value in self._arguments.items())
        original_module_path = f"{self._function.__module__}"
        return f"{_clean_module_string(original_module_path)}{self._function.__name__}({args})"


@contextmanager
def _pio_templates_default():
    """Sets pio.templates.default to "vizro_dark" and then reverts it.

    This is to ensure that in a Jupyter Notebook captured charts look the same as when they're in the dashboard. When
    the context manager exits the global theme is reverted just to keep things clean (e.g. if you really wanted to,
    you could compare a captured vs. non-captured chart in the same Python session).

    This works even if users have tweaked the templates, so long as pio.templates has been updated correctly and you
    refer to template by name rather than trying to take from vizro.themes.

    If pio.templates.default has already been set to vizro_dark or vizro_light then no change is made to allow a user
    to set these without it being overridden.
    """
    old_default = pio.templates.default
    template_changed = False
    # If the user has set pio.templates.default to a vizro theme already, no need to change it.
    if old_default not in ["vizro_dark", "vizro_light"]:
        template_changed = True
        pio.templates.default = "vizro_dark"

    # Revert the template. This is done in a try/finally so that if the code wrapped inside the context manager (i.e.
    # plotting functions) raises an exception, pio.templates.default is still reverted. This is not very important
    # but easy to achieve.
    try:
        # This will always be vizro_light or vizro_dark and corresponds to the default theme that has been set.
        yield pio.templates.default
    finally:
        if template_changed:
            pio.templates.default = old_default


class capture:
    """Captures a function call to create a [`CapturedCallable`][vizro.models.types.CapturedCallable].

    This is used to add the functionality required to make graphs and actions work in a dashboard.
    Typically, it should be used as a function decorator. There are five possible modes: `"graph"`, `"table"`,
    `"ag_grid"`, `"figure"` and `"action"`.

    Args:
        mode: The mode of the captured callable. Valid modes are `"graph"`, `"table"`, `"ag_grid"`,
            `"figure"` and `"action"`.

    Examples:
        >>> @capture("graph")
        >>> def graph_function():
        >>>     ...
        >>> @capture("table")
        >>> def table_function():
        >>>     ...
        >>> @capture("ag_grid")
        >>> def ag_grid_function():
        >>>     ...
        >>> @capture("figure")
        >>> def figure_function():
        >>>     ...
        >>> @capture("action")
        >>> def action_function():
        >>>     ...

    For further help on the use of `@capture("graph")`, you can refer to the guide on
    [custom graphs](../user-guides/custom-charts.md).
    For further help on the use of `@capture("table")` or `@capture("ag_grid")`, you can refer to the guide on
    [custom tables](../user-guides/custom-tables.md).
    For further help on the use of `@capture("figure")`, you can refer to the guide on
    [figures](../user-guides/figure.md).
    For further help on the use of `@capture("action")`, you can refer to the guide on
    [custom actions](../user-guides/custom-actions.md).

    """

    def __init__(self, mode: Literal["graph", "action", "table", "ag_grid", "figure"]):
        """Decorator to capture a function call."""
        # mode and model_example are used in later validations of the captured callable.
        self._mode = mode
        model_examples = {
            "graph": "vm.Graph(figure=...)",
            "action": "vm.Action(function=...)",
            "table": "vm.Table(figure=...)",
            "ag_grid": "vm.AgGrid(figure=...)",
            "figure": "vm.Figure(figure=...)",
        }
        self._model_example = model_examples[mode]

    def __call__(self, func, /):
        """Produces a CapturedCallable or _DashboardReadyFigure.

        mode="action" and mode="table" give a CapturedCallable, while mode="graph" gives a _DashboardReadyFigure that
        contains a CapturedCallable. In both cases, the CapturedCallable is based on func and the provided
        *args and **kwargs.
        """
        if self._mode == "graph":
            # The more difficult case, where we need to still have a valid plotly figure that renders in a notebook.
            # Hence we attach the CapturedCallable as a property instead of returning it directly.
            # TODO: move point of checking that data_frame argument exists earlier on.
            # TODO: also would be nice to raise errors in CapturedCallable.__init__ at point of function definition
            #  rather than point of calling if possible.
            @functools.wraps(func)
            def wrapped(*args, **kwargs) -> _DashboardReadyFigure:
                if "data_frame" not in inspect.signature(func).parameters:
                    raise ValueError(f"{func.__name__} must have data_frame argument to use capture('graph').")

                # We need to capture function upfront in order to find value of data_frame argument: since it could be
                # positional or keyword, this is much more robust than trying to get it out of arg or kwargs ourselves.
                captured_callable: CapturedCallable = CapturedCallable(func, *args, **kwargs)
                captured_callable._mode = self._mode
                captured_callable._model_example = self._model_example

                try:
                    captured_callable["data_frame"]
                except KeyError as exc:
                    raise ValueError(f"{func.__name__} must supply a value to data_frame argument.") from exc

                if isinstance(captured_callable["data_frame"], str):
                    # Enable running e.g. px.scatter("iris") from the Python API. Don't actually run the function
                    # because it won't work as there's no data. This case is not relevant for the JSON/YAML API,
                    # which is handled separately through validation of CapturedCallable.
                    fig = _DashboardReadyFigure()
                else:
                    # Standard case for px.scatter(df: pd.DataFrame).
                    # Set theme for the figure that gets shown in a Jupyter Notebook. This is to ensure that in a
                    # Jupyter Notebook captured charts look the same as when they're in the dashboard. To mimic this,
                    # we first use _pio_templates_default to set the global theme, as is done in the dashboard, and then
                    # do the fig.layout.template update that is achieved by the theme selector.
                    # We don't want to update the captured_callable in the same way, since it's only used inside the
                    # dashboard, at which point the global pio.templates.default is always set anyway according to
                    # the dashboard theme and then updated according to the theme selector.
                    with _pio_templates_default() as default_template:
                        fig = func(*args, **kwargs)
                    # Update the fig.layout.template just to ensure absolute consistency with how the dashboard
                    # works. In a dashboard this is done with the update_graph_theme clientside callback.
                    # The only exception here is the edge case that the user has specified template="vizro_light" or
                    # "vizro_dark" in the plotting function, in which case we don't want to change it. This makes
                    # it easier for a user to try out both themes simultaneously in a notebook.
                    if fig.layout.template not in (pio.templates["vizro_dark"], pio.templates["vizro_light"]):
                        fig.layout.template = default_template
                    fig.__class__ = _DashboardReadyFigure

                fig._captured_callable = captured_callable
                return fig

            return wrapped
        elif self._mode == "action":
            # The "normal" case where we just capture the function call.
            @functools.wraps(func)
            def wrapped(*args, **kwargs) -> CapturedCallable:
                # Note this is basically the same as partial(func, *args, **kwargs)
                captured_callable: CapturedCallable = CapturedCallable(func, *args, **kwargs)
                captured_callable._mode = self._mode
                captured_callable._model_example = self._model_example
                return captured_callable

            return wrapped
        elif self._mode in ["table", "ag_grid", "figure"]:

            @functools.wraps(func)
            def wrapped(*args, **kwargs) -> CapturedCallable:
                if "data_frame" not in inspect.signature(func).parameters:
                    raise ValueError(f"{func.__name__} must have data_frame argument to use capture('table').")

                captured_callable: CapturedCallable = CapturedCallable(func, *args, **kwargs)
                captured_callable._mode = self._mode
                captured_callable._model_example = self._model_example

                try:
                    captured_callable["data_frame"]
                except KeyError as exc:
                    raise ValueError(f"{func.__name__} must supply a value to data_frame argument.") from exc
                return captured_callable

            return wrapped
        raise ValueError(
            "Valid modes of the capture decorator are @capture('graph'), @capture('action'), @capture('table'), "
            "@capture('ag_grid') and @capture('figure')."
        )


# For "component_id.component_property", e.g. "dropdown_id.value".
_IdProperty: TypeAlias = str
"""A string that must be in the format 'component-id.component-property'."""

# Really this should be NewType and used for models like VizroBaseModel.id, but that clutters the code with casts and
# means that to get user code to type-check successfully they would need to cast to ModelID.
ModelID: TypeAlias = str
"""Represents a Vizro model ID."""

_IdOrIdProperty: TypeAlias = Union[ModelID, _IdProperty]
"""Represents either a model ID or a string in the format 'component-id.component-property'."""

# Types used for selector values and options. Note the docstrings here are rendered on the API reference.
SingleValueType = Union[StrictBool, float, str, date]
"""Permissible value types for single-value selectors. Values are displayed as default."""
MultiValueType = Union[list[StrictBool], list[float], list[str], list[date]]
"""Permissible value types for multi-value selectors. Values are displayed as default."""


class OptionsDictType(TypedDict):
    """Permissible sub-type for OptionsType. Needs to be in the format of {"label": XXX, "value": XXX}."""

    label: str
    value: SingleValueType


OptionsType = Union[list[StrictBool], list[float], list[str], list[date], list[OptionsDictType]]
"""Permissible options types for selectors. Options are available choices for user to select from."""

# All the below types rely on models and so must use ForwardRef (i.e. "Checklist" rather than actual Checklist class).
SelectorType = Annotated[
    Union["Checklist", "DatePicker", "Dropdown", "RadioItems", "RangeSlider", "Slider"],
    Field(discriminator="type", description="Selectors to be used inside a control."),
]
"""Discriminated union. Type of selector to be used inside a control: [`Checklist`][vizro.models.Checklist],
[`DatePicker`][vizro.models.DatePicker], [`Dropdown`][vizro.models.Dropdown], [`RadioItems`][vizro.models.RadioItems],
[`RangeSlider`][vizro.models.RangeSlider] or [`Slider`][vizro.models.Slider]."""

_FormComponentType = Annotated[
    Union[SelectorType, "Button", "UserInput"],
    Field(discriminator="type", description="Components that can be used to receive user input within a form."),
]

ControlType = Annotated[
    Union["Filter", "Parameter"],
    Field(discriminator="type", description="Control that affects components on the page."),
]
"""Discriminated union. Type of control that affects components on the page: [`Filter`][vizro.models.Filter] or
[`Parameter`][vizro.models.Parameter]."""

ComponentType = Annotated[
    Union["AgGrid", "Button", "Card", "Container", "Figure", "Graph", "Text", "Table", "Tabs"],
    Field(
        discriminator="type",
        description="Component that makes up part of the layout on the page.",
    ),
]
"""Discriminated union. Type of component that makes up part of the layout on the page:
[`Button`][vizro.models.Button], [`Card`][vizro.models.Card], [`Table`][vizro.models.Table],
[`Graph`][vizro.models.Graph] or [`AgGrid`][vizro.models.AgGrid]."""

NavPagesType = Union[list[ModelID], dict[str, list[ModelID]]]
"List of page IDs or a mapping from name of a group to a list of page IDs (for hierarchical sub-navigation)."

NavSelectorType = Annotated[
    Union["Accordion", "NavBar"], Field(discriminator="type", description="Component for rendering navigation.")
]
"""Discriminated union. Type of component for rendering navigation:
[`Accordion`][vizro.models.Accordion] or [`NavBar`][vizro.models.NavBar]."""

LayoutType = Annotated[
    Union[Annotated["Grid", Tag("grid")], Annotated["Flex", Tag("flex")], Annotated["Layout", Tag("legacy_layout")]],
    Field(
        discriminator=Discriminator(_get_layout_discriminator),
        description="Type of layout to place components on the page.",
    ),
]
"""Discriminated union. Type of layout to place components on the page:
[`Grid`][vizro.models.Grid] or [`Flex`][vizro.models.Flex]."""

# JSONSchema should be skipped for private actions that are not part of the public API.
# In addition, `_filter` doesn't have a well defined schema due the Callables,
# so if we were to include it, the JSONSchema would need to be defined.
# TODO: Note that atm ActionType violates our (and pydantic's) convention that the type of the model ensures
# the type AFTER validation. Since ActionType is used as annotation for the actions field,
# this is not true as long as we convert to ActionsChain.
ActionType = Annotated[
    Union[
        Annotated["Action", Tag("action")],
        Annotated["export_data", Tag("export_data")],
        Annotated["filter_interaction", Tag("filter_interaction")],
        SkipJsonSchema[Annotated["_filter", Tag("_filter")]],
        SkipJsonSchema[Annotated["_parameter", Tag("_parameter")]],
        SkipJsonSchema[Annotated["_on_page_load", Tag("_on_page_load")]],
    ],
    Field(discriminator=Discriminator(_get_action_discriminator), description="Action."),
]
"""Discriminated union. Type of action: [`Action`][vizro.models.Action], [`export_data`][vizro.models.export_data] or [
`filter_interaction`][vizro.models.filter_interaction]."""

# Extra type groups used for mypy casting
FigureWithFilterInteractionType = Union["Graph", "Table", "AgGrid"]
FigureType = Union["Graph", "Table", "AgGrid", "Figure"]


# TODO-AV2 A 1: improve this structure. See https://github.com/mckinsey/vizro/pull/880.
# Remember filter_interaction won't be here in future.
class _Controls(TypedDict):
    filters: list[Any]
    parameters: list[Any]
    filter_interaction: list[dict[str, Any]]
