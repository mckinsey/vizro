"""Types used in pydantic fields."""

# ruff: noqa: F821
from __future__ import annotations

import functools
import inspect
from datetime import date
from typing import Any, Dict, List, Literal, Protocol, Union, runtime_checkable

try:
    from pydantic.v1 import Field, StrictBool
    from pydantic.v1.fields import ModelField
    from pydantic.v1.schema import SkipField
except ImportError:  # pragma: no cov
    from pydantic import Field, StrictBool
    from pydantic.fields import ModelField
    from pydantic.schema import SkipField

from typing_extensions import Annotated, TypedDict

from vizro.charts._charts_utils import _DashboardReadyFigure


# Used to describe _DashboardReadyFigure so we can keep CapturedCallable generic rather than referring to
# _DashboardReadyFigure explicitly.
@runtime_checkable
class _SupportsCapturedCallable(Protocol):
    _captured_callable: CapturedCallable


class CapturedCallable:
    """Stores a captured function call to use in a dashboard.

    Users do not need to instantiate this class directly. Instances are instead generated automatically
    through the [`capture`][vizro.models.types.capture] decorator. Some of the functionality is similar to
    `functools.partial`.

    Ready-to-use `CapturedCallable` instances are provided by Vizro. In this case refer to the [user guide on
    Charts/Graph](../user-guides/graph.md), [Table](../user-guides/table.md) or [Actions](../user-guides/actions.md)
    to see available choices.

    (Advanced) In case you would like to create your own `CapturedCallable`, please refer to the [user guide on
    custom charts](../user-guides/custom-charts.md),
    [custom tables](../user-guides/custom-tables.md) or
    [custom actions](../user-guides/custom-actions.md).
    """

    def __init__(self, function, /, *args, **kwargs):
        """Creates a new `CapturedCallable` object that will be able to re-run `function`.

        Partially binds *args and **kwargs to the function call.

        Raises
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

        # This is used to check that the mode of the capture decorator matches the inserted captured callable.
        self._mode = None

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

    def __delitem__(self, arg_name: str):
        """Deletes a bound argument."""
        del self.__bound_arguments[arg_name]

    @property
    def _arguments(self):
        # TODO: This is used twice: in _get_parametrized_config and in vm.Action and should be removed when those
        # references are removed.
        return self.__bound_arguments

    # TODO-actions: Find a way how to compare CapturedCallable and function
    @property
    def _function(self):
        return self.__function

    @classmethod
    def __get_validators__(cls):
        """Makes type compatible with pydantic model without needing `arbitrary_types_allowed`."""
        yield cls._parse_json

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any], field: ModelField):
        """Generates schema for field of this type."""
        raise SkipField(f"{cls.__name__} {field.name} is excluded from the schema.")

    @classmethod
    def _parse_json(
        cls, callable_config: Union[_SupportsCapturedCallable, CapturedCallable, Dict[str, Any]], field: ModelField
    ) -> CapturedCallable:
        """Parses callable_config specification from JSON/YAML to a CapturedCallable.

        This uses the hydra syntax for _target_ but none of the other bits and we don't actually use hydra
        to implement it. In future, we might like to switch to using hydra's actual implementation
        which would allow nested functions (e.g. for transformers?) and to specify the path to a _target_ that lives
        outside of vizro.plotly_express. See https://hydra.cc/docs/advanced/instantiate_objects/overview/.
        """
        if isinstance(callable_config, CapturedCallable):
            # e.g. an action function that is already CapturedCallable
            return callable_config
        elif isinstance(callable_config, _SupportsCapturedCallable):
            # e.g. a _DashboardReadyFigure that has CapturedCallable in a property ._captured_callable
            return callable_config._captured_callable
        elif not isinstance(callable_config, dict):
            raise ValueError(
                "You must provide a valid CapturedCallable object. If you are using a plotly express figure, ensure "
                "that you are using `import vizro.plotly.express as px`. If you are using a table figure, make "
                "sure you are using `from vizro.tables import dash_data_table`. If you are using a custom figure or "
                "action, that your function uses the @capture decorator."
            )

        # Try to import function given in _target_ from the import_path property of the pydantic field.
        try:
            function_name = callable_config.pop("_target_")
        except KeyError as exc:
            raise ValueError(
                "CapturedCallable object must contain the key '_target_' that gives the target function."
            ) from exc

        import_path = field.field_info.extra["import_path"]
        try:
            function = getattr(import_path, function_name)
        except AttributeError as exc:
            raise ValueError(f"_target_={function_name} cannot be imported from {import_path.__name__}.") from exc

        # All the other items in figure are the keyword arguments to pass into function.
        function_kwargs = callable_config

        # It would seem natural to return cls(function, **function_kwargs) here, but the function is already decorated
        # with @capture, and so that would return a nested CapturedCallable.
        captured_callable = function(**function_kwargs)
        if isinstance(captured_callable, CapturedCallable):
            # e.g. an action function that is already CapturedCallable
            return captured_callable
        elif isinstance(captured_callable, _SupportsCapturedCallable):
            # e.g. a _DashboardReadyFigure that has CapturedCallable in a property ._captured_callable
            return captured_callable._captured_callable
        else:
            raise ValueError(f"_target_={function_name} must be wrapped in the @capture decorator.")


class capture:
    """Captures a function call to create a [`CapturedCallable`][vizro.models.types.CapturedCallable].

    This is used to add the functionality required to make graphs and actions work in a dashboard.
    Typically, it should be used as a function decorator. There are four possible modes: `"graph"`, `"table"`,
    `"ag_grid"` and `"action"`.

    Examples
        >>> @capture("graph")
        >>> def graph_function():
        >>>     ...
        >>> @capture("table")
        >>> def table_function():
        >>>     ...
        >>> @capture("ag_grid")
        >>> def ag_grid_function():
        >>>     ...
        >>> @capture("action")
        >>> def action_function():
        >>>     ...

    For further help on the use of `@capture("graph")`, you can refer to the guide on
    [custom graphs](../user-guides/custom-charts.md).
    For further help on the use of `@capture("table")` or `@capture("ag_grid")`, you can refer to the guide on
    [custom tables](../user-guides/custom-tables.md).
    For further help on the use of `@capture("action")`, you can refer to the guide on
    [custom actions](../user-guides/custom-actions.md).

    """

    def __init__(self, mode: Literal["graph", "action", "table", "ag_grid"]):
        """Decorator to capture a function call. Valid modes are "graph", "table", "action" and "ag_grid"."""
        self._mode = mode

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
                    fig = func(*args, **kwargs)
                    fig.__class__ = _DashboardReadyFigure

                fig._captured_callable = captured_callable
                return fig

            return wrapped
        elif self._mode == "action":
            # The "normal" case where we just capture the function call.
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                # Note this is basically the same as partial(func, *args, **kwargs)
                captured_callable: CapturedCallable = CapturedCallable(func, *args, **kwargs)
                captured_callable._mode = self._mode
                return captured_callable

            return wrapped
        elif self._mode in ["table", "ag_grid"]:

            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                if "data_frame" not in inspect.signature(func).parameters:
                    raise ValueError(f"{func.__name__} must have data_frame argument to use capture('table').")

                captured_callable: CapturedCallable = CapturedCallable(func, *args, **kwargs)
                captured_callable._mode = self._mode

                try:
                    captured_callable["data_frame"]
                except KeyError as exc:
                    raise ValueError(f"{func.__name__} must supply a value to data_frame argument.") from exc
                return captured_callable

            return wrapped
        raise ValueError(
            "Valid modes of the capture decorator are @capture('graph'), @capture('action'), @capture('table') or "
            "@capture('ag_grid')."
        )


# Types used for selector values and options. Note the docstrings here are rendered on the API reference.
SingleValueType = Union[StrictBool, float, str, date]
"""Permissible value types for single-value selectors. Values are displayed as default."""
MultiValueType = Union[List[StrictBool], List[float], List[str], List[date]]
"""Permissible value types for multi-value selectors. Values are displayed as default."""


class OptionsDictType(TypedDict):
    """Permissible sub-type for OptionsType. Needs to be in the format of {"label": XXX, "value": XXX}."""

    label: str
    value: SingleValueType


OptionsType = Union[List[StrictBool], List[float], List[str], List[date], List[OptionsDictType]]
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
    Union["AgGrid", "Button", "Card", "Container", "Graph", "Table", "Tabs"],
    Field(
        discriminator="type",
        description="Component that makes up part of the layout on the page.",
    ),
]
"""Discriminated union. Type of component that makes up part of the layout on the page:
[`Button`][vizro.models.Button], [`Card`][vizro.models.Card], [`Table`][vizro.models.Table],
[`Graph`][vizro.models.Graph] or [`AgGrid`][vizro.models.AgGrid]."""

NavPagesType = Union[List[str], Dict[str, List[str]]]
"List of page IDs or a mapping from name of a group to a list of page IDs (for hierarchical sub-navigation)."

NavSelectorType = Annotated[
    Union["Accordion", "NavBar"], Field(discriminator="type", description="Component for rendering navigation.")
]
"""Discriminated union. Type of component for rendering navigation:
[`Accordion`][vizro.models.Accordion] or [`NavBar`][vizro.models.NavBar]."""
