"""Types used in pydantic fields."""
# ruff: noqa: F821
from __future__ import annotations

import functools
import inspect
from typing import Any, Dict, List, Literal, Protocol, Union, runtime_checkable

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

    Ready-to-use `CapturedCallable` instances are provided by Vizro. In this case refer to the user guide on
    [Charts/Graph][graph], [Table][table] or [Actions][pre-defined-actions] to see available choices.

    (Advanced) In case you would like to create your own `CapturedCallable`, please refer to the user guide on
    [custom charts](../user_guides/custom_charts.md), [custom tables][custom-table] or
    [custom actions][custom-actions].
    """

    def __init__(self, function, /, *args, **kwargs):
        """Creates a new CapturedCallable object that will be able to re-run `function`.

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
        self.__arguments = inspect.signature(function).bind_partial(*args, **kwargs).arguments

        # A function can only ever have one variadic keyword parameter. {""} is just here so that var_keyword_param
        # is always unpacking a one element set.
        (var_keyword_param,) = {
            param.name for param in parameters.values() if param.kind == inspect.Parameter.VAR_KEYWORD
        } or {""}

        # Since we do __call__ as self.__function(**bound_arguments.arguments), we need to restructure the arguments
        # a bit to put the kwargs in the right place.
        # For a function with parameter **kwargs this converts self.__arguments = {"kwargs": {"a": 1}} into
        # self.__arguments = {"a": 1}.
        if var_keyword_param in self.__arguments:
            self.__arguments.update(self.__arguments[var_keyword_param])
            del self.__arguments[var_keyword_param]

    def __call__(self, **kwargs):
        """Run the `function` with the initial arguments overridden by **kwargs.

        Note *args are not possible here, but you can still override positional arguments using argument name.
        """
        return self.__function(**{**self.__arguments, **kwargs})

    def __getitem__(self, arg_name: str):
        """Gets the value of a bound argument."""
        return self.__arguments[arg_name]

    def __delitem__(self, arg_name: str):
        """Deletes a bound argument."""
        del self.__arguments[arg_name]

    @property
    def _arguments(self):
        # TODO: This is used twice: in _get_parametrized_config and in vm.Action and should be removed when those
        # references are removed.
        return self.__arguments

    # TODO-actions: Find a way how to compare CapturedCallable and function
    @property
    def _function(self):
        return self.__function

    @classmethod
    def __get_validators__(cls):
        """Makes type compatible with pydantic model without needing arbitrary_types_allowed."""
        yield cls._parse_json

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any], field: ModelField):
        """Generates schema for field of this type."""
        raise SkipField(f"{cls.__name__} {field.name} is excluded from the schema.")

    @classmethod
    def _parse_json(
        cls,
        callable_config: Union[_SupportsCapturedCallable, CapturedCallable, Dict[str, Any]],
        field: ModelField,
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
    Typically it should be used as a function decorator. There are three possible modes: `"graph"`, `"table"` and
    `"action"`.

    Examples:
        >>> @capture("graph")
        >>> def graph_function():
        >>>     ...
        >>> @capture("table")
        >>> def table_function():
        >>>     ...
        >>> @capture("table")
        >>> def plot_function():
        >>>     ...
        >>> @capture("action")
        >>> def action_function():
        >>>     ...

    For further help on the use of `@capture("graph")`, you can refer to the guide on
    [custom charts](../user_guides/custom_charts.md).
    """

    def __init__(self, mode: Literal["graph", "action", "table"]):
        """Instantiates the decorator to capture a function call. Valid modes are "graph", "table" and "action"."""
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

                try:
                    captured_callable["data_frame"]
                except KeyError as exc:
                    raise ValueError(f"{func.__name__} must supply a value to data_frame argument.") from exc

                if isinstance(captured_callable["data_frame"], str):
                    # Enable running e.g. px.scatter("iris") from the Python API. Don't actually run the function
                    # because it won't get work as there's no data. It's vital we don't fetch data from the data manager
                    # yet either, because otherwise all lazy data will be loaded before the dashboard is started.
                    # This case is not relevant for the JSON/YAML API, which is handled separately through validation of
                    # CapturedCallable.
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
                return CapturedCallable(func, *args, **kwargs)

            return wrapped
        elif self._mode == "table":

            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                if "data_frame" not in inspect.signature(func).parameters:
                    raise ValueError(f"{func.__name__} must have data_frame argument to use capture('table').")

                captured_callable: CapturedCallable = CapturedCallable(func, *args, **kwargs)

                try:
                    captured_callable["data_frame"]
                except KeyError as exc:
                    raise ValueError(f"{func.__name__} must supply a value to data_frame argument.") from exc
                return captured_callable

            return wrapped
        raise ValueError(
            "Valid modes of the capture decorator are @capture('graph'), @capture('action') or @capture('table')."
        )


# Types used for selector values and options. Note the docstrings here are rendered on the API reference.
SingleValueType = Union[StrictBool, float, str]
"""Permissible value types for single-value selectors. Values are displayed as default."""
MultiValueType = Union[List[StrictBool], List[float], List[str]]
"""Permissible value types for multi-value selectors. Values are displayed as default."""


class OptionsDictType(TypedDict):
    """Permissible sub-type for OptionsType. Needs to be in the format of {"label": XXX, "value": XXX}."""

    label: str
    value: SingleValueType


OptionsType = Union[List[StrictBool], List[float], List[str], List[OptionsDictType]]
"""Permissible options types for selectors. Options are available choices for user to select from."""

# All the below types rely on models and so must use ForwardRef (i.e. "Checklist" rather than actual Checklist class).
SelectorType = Annotated[
    Union["Checklist", "Dropdown", "RadioItems", "RangeSlider", "Slider"],
    Field(
        discriminator="type",
        description="Selectors to be used inside a control.",
    ),
]
"""Discriminated union. Type of selector to be used inside a control: [`Checklist`][vizro.models.Checklist],
[`Dropdown`][vizro.models.Dropdown], [`RadioItems`][vizro.models.RadioItems],
[`RangeSlider`][vizro.models.RangeSlider] or [`Slider`][vizro.models.Slider]."""

_FormComponentType = Annotated[
    Union[SelectorType, "Button", "UserInput"],
    Field(
        discriminator="type",
        description="Components that can be used to receive user input within a form'.",
    ),
]

ControlType = Annotated[
    Union["Filter", "Parameter"],
    Field(
        discriminator="type",
        description="Control that affects components on the page.",
    ),
]
"""Discriminated union. Type of control that affects components on the page: [`Filter`][vizro.models.Filter] or
[`Parameter`][vizro.models.Parameter]."""

ComponentType = Annotated[
    Union["Button", "Card", "Graph", "Table"],
    Field(
        discriminator="type",
        description="Component that makes up part of the layout on the page.",
    ),
]
"""Discriminated union. Type of component that makes up part of the layout on the page:
[`Button`][vizro.models.Button], [`Card`][vizro.models.Card], [`Table`][vizro.models.Table] or
[`Graph`][vizro.models.Graph]."""

# Types used for pages values in the Navigation model.
NavigationPagesType = Annotated[
    Union[List[str], Dict[str, List[str]]],
    Field(
        None,
        description="List of Page IDs or dict mapping of Page IDs and titles (for hierarchical sub-navigation)",
    ),
]
"""Permissible value types for page attribute. Values are displayed as default."""
