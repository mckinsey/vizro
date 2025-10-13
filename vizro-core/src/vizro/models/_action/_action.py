from __future__ import annotations

import inspect
import logging
import re
import time
import warnings
from collections.abc import Collection, Iterable, Mapping
from pprint import pformat
from typing import TYPE_CHECKING, Annotated, Any, Callable, ClassVar, Literal, Union, cast

from dash import ClientsideFunction, Input, Output, State, callback, clientside_callback, dcc, no_update
from dash.development.base_component import Component
from pydantic import BeforeValidator, Field, PrivateAttr, TypeAdapter, field_validator
from pydantic.json_schema import SkipJsonSchema
from typing_extensions import TypedDict

from vizro.managers._model_manager import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call, make_deprecated_field_warning
from vizro.models.types import (
    CapturedCallable,
    ControlType,
    FigureWithFilterInteractionType,
    OutputsType,
    _IdOrIdProperty,
    _IdProperty,
    validate_captured_callable,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from vizro.actions import export_data, filter_interaction


# TODO-AV2 A 1: improve this structure. See https://github.com/mckinsey/vizro/pull/880.
# Remember filter_interaction won't be here in future.
class ControlsStates(TypedDict):
    filters: list[State]
    parameters: list[State]
    filter_interaction: list[dict[str, State]]


class _BaseAction(VizroBaseModel):
    # The common interface shared between Action and _AbstractAction all raise NotImplementedError or are ClassVar.
    # This mypy type-check this class.
    # function and outputs are overridden as fields in Action and abstract methods in _AbstractAction. Using ClassVar
    # for these is the easiest way to appease mypy and have something that actually works at runtime.
    function: ClassVar[Callable[..., Any]]
    outputs: ClassVar[OutputsType]

    # These are set in the make_actions_chain validator (same for both Action and _AbstractAction).
    # In the future a user would probably be able to specify something here that would look up a key in
    # _action_triggers or just a full _IdProperty. The _first_in_chain_trigger and _prevent_initial_call_of_guard would
    # remain private though. These are required for correct functioning of the actions chain guard.
    _trigger: _IdProperty = PrivateAttr()
    _first_in_chain_trigger: _IdProperty = PrivateAttr()
    _prevent_initial_call_of_guard: bool = PrivateAttr()

    # Temporary workaround for lookups in filter_interaction and set_control. This should become unnecessary once
    # the model manager supports `parent_model` access for all Vizro models.
    _parent_model: VizroBaseModel = PrivateAttr()

    @property
    def _is_first_in_chain(self) -> bool:
        """Whether this action is the first in the chain of actions."""
        return self._first_in_chain_trigger == self._trigger

    @property
    def _dash_components(self) -> list[Component]:
        """Internal components needed to run the actions chain system.

        Includes:
        - {action.id}_finished for completion of an action callback to trigger the next action in the chain
        - {action.id}_guarded_trigger for the first action in a chain so that guard_action_chain callback prevent
            undesired triggering (workaround for Dash prevent_initial_call=True behavior)

        In theory, subclasses can add additional components to the list, as done in export_data, but this should not be
        generally encouraged. In the future it might not be possible.
        """
        dash_components = [dcc.Store(id=f"{self.id}_finished")]
        if self._is_first_in_chain:
            # Only need the guard for the first action in the chain.
            dash_components.append(dcc.Store(id=f"{self.id}_guarded_trigger"))

        return dash_components

    @property
    def _legacy(self):
        raise NotImplementedError

    @property
    def _parameters(self) -> set[str]:
        raise NotImplementedError

    @property
    def _runtime_args(self) -> dict[str, _IdOrIdProperty]:
        raise NotImplementedError

    @property
    def _action_name(self) -> str:
        raise NotImplementedError

    @property
    def _validated_outputs(self) -> OutputsType:
        raise NotImplementedError

    def _get_control_states(self, control_type: ControlType) -> list[State]:
        """Gets list of `States` for selected `control_type` that appear on page where this Action is defined."""
        # Possibly the code that specifies the state associated with a control will move to an inputs property
        # of the filter and parameter models in future. This property could match outputs and return just a dotted
        # string that is then transformed to State inside _transformed_inputs. This would prevent us from using
        # pattern-matching callback here though.
        # Maybe want to revisit this as part of TODO-AV2 A 1.
        page = model_manager._get_model_page(self)
        return [
            State(*control.selector._action_inputs["__default__"].split("."))
            for control in cast(Iterable[ControlType], model_manager._get_models(control_type, page))
        ]

    def _get_filter_interaction_states(self) -> list[dict[str, State]]:
        """Gets list of `States` for selected chart interaction `filter_interaction`."""
        from vizro.actions import filter_interaction

        page = model_manager._get_model_page(self)

        # States are stored in the parent model (e.g. AgGrid) whose actions contains the filter_interaction rather than
        # the filter_interaction model itself, hence needing to lookup action._parent_model.
        # This is also needed to trigger the parent model's `_get_value_from_trigger` method in set_control.
        # After work on the model_manager we should be able to tidy this to directly get the parent model
        # from inside the action.
        # Maybe want to revisit this as part of TODO-AV2 A 1.
        return [
            cast(FigureWithFilterInteractionType, action._parent_model)._filter_interaction_input
            for action in model_manager._get_models(filter_interaction, page)
        ]

    @staticmethod
    def _transform_dependency(dependency: _IdOrIdProperty, type: Literal["output", "input"]) -> _IdProperty:
        """Transform a component dependency into its mapped property value.

        This method handles two formats of component dependencies:
        1. Explicit format: "component-id.component-property" (e.g. "graph-1.figure")
           - Returns the mapped value if it exists in the component's _action_outputs/_action_inputs
           - Returns the original dependency otherwise
        2. Implicit format: "component-id" (e.g. "card-id")
           - Returns the value of "__default__" key from the component's _action_outputs/_action_inputs
           - Raises an error if the component doesn't exist or doesn't have the required property

        Args:
            dependency: A string in either "component-id.component-property" or "component-id" format
            type: Either "input" or "output" to determine which property (_action_inputs or _action_outputs) to check

        Returns:
            The mapped property value for implicit format, or the original dependency for explicit format

        Raises:
            KeyError: If component does not exist in model_manager
            KeyError: If component exists but has no "__default__" key in its _action_outputs/_action_inputs
            AttributeError: If component exists but has no _action_outputs/_action_inputs property defined
            ValueError: If dependency format is invalid (e.g. "id.prop.prop" or "id..prop")
        """
        attribute_type = "_action_outputs" if type == "output" else "_action_inputs"

        # Validate that the dependency is in one of two valid formats: id.property ("graph-1.figure") or id ("card-id").
        # By this point we have already validation dependency is a str.
        if not re.match(r"^[^.]+$|^[^.]+[.][^.]+$", dependency):
            raise ValueError(
                f"Invalid {type} format '{dependency}'. Expected format is '<model_id>' or "
                f"'<model_id>.<argument_name>'."
            )

        if "." in dependency:
            component_id, component_property = dependency.split(".")
            try:
                return getattr(model_manager[component_id], attribute_type)[component_property]
            except (KeyError, AttributeError):
                # Captures these cases and returns dependency unchanged, as we want to allow the user to target
                # Dash components, that are not registered in the model_manager (e.g. theme-selector).
                # 1. component_id is not in model_manager
                # 2. component doesn't have _action_outputs/_action_inputs defined
                # 3. component_property is not in the _action_outputs/inputs dictionary
                return dependency

        component_id, component_property = dependency, "__default__"

        try:
            return getattr(model_manager[component_id], attribute_type)[component_property]
        except (KeyError, AttributeError) as exc:
            if isinstance(exc, KeyError):
                if component_property in str(exc):
                    raise KeyError(
                        f"Model with ID `{component_id}` has no `{component_property}` key inside its "
                        f"`{attribute_type}` property. Please specify the {type} explicitly as "
                        f"`{component_id}.<property>`."
                    ) from exc
                raise KeyError(
                    f"Model with ID `{component_id}` not found. Please provide a valid component ID."
                ) from exc
            raise AttributeError(
                f"Model with ID '{component_id}' does not have implicit {type} properties defined. "
                f"Please specify the {type} explicitly as '{component_id}.<property>'."
            ) from exc

    @property
    def _transformed_inputs(self) -> Union[list[State], dict[str, Union[State, ControlsStates]]]:
        """Creates Dash States given the user-specified runtime arguments and built in ones.

        Return type is list only for legacy actions. Otherwise, it will always be a dictionary (unlike
        for _transformed_outputs, where new behavior can still give a list). Keys are the parameter names. For
        user-specified inputs, values are Dash States. For built-in inputs, values can be more complicated nested
        structure of states.
        """
        if self._legacy:
            # Must be an Action rather than _AbstractAction, so has already been validated by pydantic field annotation.
            return [
                State(*self._transform_dependency(input, type="input").split("."))
                for input in cast(Action, self).inputs
            ]

        from vizro.models import Filter, Parameter

        builtin_args = {
            "_controls": {
                "filters": self._get_control_states(control_type=Filter),
                "parameters": self._get_control_states(control_type=Parameter),
                "filter_interaction": self._get_filter_interaction_states(),
            },
            "_trigger": State(*self._first_in_chain_trigger.split(".")),
        }

        # Work out which built in arguments are actually required for this function.
        builtin_args = {
            arg_name: arg_value for arg_name, arg_value in builtin_args.items() if arg_name in self._parameters
        }

        # Validate that the runtime arguments are in the same form as the legacy Action.inputs field (str).
        # Currently, this code only runs for subclasses of _AbstractAction but not vm.Action instances because a
        # vm.Action that does not pass this check will have already been classified as legacy in Action._legacy.
        # In future when vm.Action.inputs is removed then this will be used for vm.Action instances also.
        TypeAdapter(dict[str, str]).validate_python(self._runtime_args)
        # User specified arguments runtime_args take precedence over built in reserved arguments. No static arguments
        # ar relevant here, just Dash States. Static arguments values are stored in the state of the relevant
        # _AbstractAction instance.
        runtime_args = {
            arg_name: State(*self._transform_dependency(arg_value, type="input").split("."))
            for arg_name, arg_value in self._runtime_args.items()
        }

        return builtin_args | runtime_args

    @property
    def _transformed_outputs(self) -> Union[list[Output], dict[str, Output]]:
        """Creates Dash Output objects from string specifications in self.outputs.

        Converts self._validated_outputs (list of strings or dictionary of strings where each string is in the
        format '<component_id>.<property>' or '<component_id>') and converts into Dash Output objects.
        For example, 'my_graph.figure' or ['my_graph.figure'] becomes
            [Output(component_id='my_graph', component_property='figure', allow_duplicate=True)].

        Returns:
            Union[list[Output], dict[str, Output]]: A list of Output objects if self.outputs is a list of strings,
            or a dictionary mapping keys to Output objects if self.outputs is a dictionary of strings.
        """

        def _transform_output(output):
            # Action.outputs is already validated by pydantic as list[str] or dict[str, str]
            # _AbstractAction._transformed_outputs does the same validation manually with TypeAdapter.
            return Output(*self._transform_dependency(output, type="output").split("."), allow_duplicate=True)

        # By this point self._validated_outputs is guaranteed to be OutputsType i.e. list[str] or dict[str, str].
        # A single str value will have been coerced to list already.
        if isinstance(self._validated_outputs, list):
            callback_outputs = [_transform_output(output) for output in self._validated_outputs]

            # Need to use a single Output in the @callback decorator rather than a single element list for the case
            # of a single output. This means the action function can return a single value (e.g. "text") rather than a
            # single element list (e.g. ["text"]).
            if len(callback_outputs) == 1:
                [callback_outputs] = callback_outputs
            return callback_outputs

        return {output_name: _transform_output(output) for output_name, output in self._validated_outputs.items()}

    def _action_callback_function(
        self,
        inputs: Union[dict[str, Any], list[Any]],
        outputs: Union[dict[str, Output], list[Output], Output, None],
    ) -> Any:
        logger.debug("===== Running action with id %s, function %s =====", self.id, self._action_name)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Action inputs:\n%s", pformat(inputs, depth=3, width=200))
            logger.debug("Action outputs:\n%s", pformat(outputs, width=200))

        if self._legacy:
            # Inputs must be list[str].
            return_value = cast(Action, self).function(*inputs)  # type: ignore[operator]
        else:
            return_value = self.function(**inputs)  # type: ignore[arg-type]

        # Delegate all handling of the return_value and mapping to appropriate outputs to Dash - we don't modify
        # return_value to reshape it in any way. All we do is do some error checking to raise clearer error messages.
        if not outputs:
            if return_value is not None:
                raise ValueError("Action function has returned a value but the action has no defined outputs.")
        elif isinstance(outputs, dict):
            if not isinstance(return_value, Mapping):
                raise ValueError(
                    "Action function has not returned a dictionary-like object "
                    "but the action's defined outputs are a dictionary."
                )
            if set(outputs) != set(return_value):
                raise ValueError(
                    f"Keys of action's returned value {set(return_value) or {}} "
                    f"do not match the action's defined outputs {set(outputs) or {}})."
                )
        elif isinstance(outputs, list):
            if not isinstance(return_value, Collection):
                raise ValueError(
                    "Action function has not returned a list-like object but the action's defined outputs are a list."
                )
            if len(return_value) != len(outputs):
                raise ValueError(
                    f"Number of action's returned elements {len(return_value)} does not match the number"
                    f" of action's defined outputs {len(outputs)}."
                )

        # If no error has been raised then the return_value is good and is returned as it is.
        # This could be a list of outputs, dictionary of outputs or any single value including None.
        return return_value

    @_log_call
    def _define_callback(self):
        """Defines a callback for the Action model."""
        external_callback_inputs = self._transformed_inputs
        external_callback_outputs = self._transformed_outputs

        if self._is_first_in_chain:
            # If the action is the first one in the action chain then we need to insert an additional "guard"
            # callback. This prevents the main action callback (action_callback) firing even in the case that the
            # Input component is created in the layout. This is a workaround for the behavior of
            # prevent_initial_call=True which otherwise does not prevent initial callback execution when
            # an Input component appears if an Output already exists in the page layout:
            # https://dash.plotly.com/advanced-callbacks#prevent-callback-execution-upon-initial-component-render
            # e.g. for the case of a dynamic filter, we want the guard to let through genuine callback triggers (user
            # changes value of filter) vs. when the dropdown is created. This works as follows:
            #   1. When a new dynamic component is created, a dcc.Store component labeled *_guard_actions_chain
            #   is created at the same time with data=True.
            #   2. When guard_action_chain callback is triggered, we work out whether the trigger of the callback
            #   chain is genuine or not:
            #      - if it's due to creation of component then we do not allow action chain to execute. This mimics
            #        what prevent_initial_call=True on action_callback would ideally do.
            #      - if it's genuine then we allow action chain to execute
            # The guard is needed only for the first action in the chain because subsequent actions can only be
            # triggered by the *_finished dcc.Store which cannot be accidentally triggered since it's created fresh
            # on every page.
            trigger_component_id = self._trigger.split(".")[0]
            component_guard_id = f"{trigger_component_id}_guard_actions_chain"
            trigger = Input(f"{self.id}_guarded_trigger", "data")

            # We want prevent_initial_call=True for all but the on page load callback. This means that the on page load
            # callback goes through the same gateway system as everything else and will run when the page layout is
            # generated.
            # An alternative method would be to always set prevent_initial_call=True and trick Dash into still running
            # the guard_action_chain by putting the Output in the global dashboard page layout, but changing
            # prevent_initial_call feels cleaner since it means the dcc.Stores do not need to be split between page-
            # and dashboard- level.
            clientside_callback(
                ClientsideFunction(namespace="action", function_name="guard_action_chain"),
                Output(f"{self.id}_guarded_trigger", "data"),
                Input(*self._trigger.split(".")),
                State(component_guard_id, "data", allow_optional=True),
                State(trigger_component_id, "id"),
                prevent_initial_call=self._prevent_initial_call_of_guard,
            )
        else:
            trigger = Input(*self._trigger.split("."))

        callback_inputs = {"external": external_callback_inputs, "internal": {"trigger": trigger}}
        callback_outputs: dict[str, Union[list[Output], dict[str, Output]]] = {
            "internal": {
                "action_finished": Output(f"{self.id}_finished", "data"),
                "action_progress_indicator": Output(
                    "action-progress-indicator-placeholder", "children", allow_duplicate=True
                ),
            },
        }

        # If there are no outputs then we don't want the external part of callback_outputs to exist at all.
        # This allows the action function to return None and match correctly on to the callback_outputs dictionary
        # The (probably better) alternative to this would be just to define a dummy output for all such functions
        # so that the external key always exists.
        # Note that it's still possible to explicitly return None as a value when an output is specified.
        if external_callback_outputs:
            callback_outputs["external"] = external_callback_outputs

        logger.debug(
            "===== Defining callback for Action with id %s, function %s =====",
            self.id,
            self._action_name,
        )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Callback inputs:\n%s", pformat(callback_inputs["external"], width=200))
            logger.debug("Callback outputs:\n%s", pformat(callback_outputs.get("external"), width=200))

        @callback(output=callback_outputs, inputs=callback_inputs, prevent_initial_call=True)
        def action_callback(external: Union[list[Any], dict[str, Any]], internal: dict[str, Any]) -> dict[str, Any]:
            external_return = self._action_callback_function(inputs=external, outputs=callback_outputs.get("external"))
            return_value = {
                "internal": {
                    "action_finished": time.time(),
                    "action_progress_indicator": no_update,
                }
            }
            if "external" in callback_outputs:
                return_value["external"] = external_return

            return return_value


class Action(_BaseAction):
    """Custom action to be inserted into `actions` of relevant component.

    Abstract: Usage documentation
        [How to create custom actions](../user-guides/custom-actions.md)

    Args:
        function (CapturedCallable): Custom action function.
        inputs (list[str]): List of inputs provided to the action function. Each input can be specified as
            `<model_id>` or `<model_id>.<argument_name>` or `<component_id>.<property>`. Defaults to `[]`.
            ❗Deprecated: `inputs` is deprecated and [will not exist in Vizro 0.2.0](
            deprecations.md#action-model-inputs-argument).
        outputs (OutputsType): See [`OutputsType`][vizro.models.types.OutputsType].
    """

    # TODO-AV2 D 5: when it's made public, add something like below to docstring:
    # This class is only relevant for user-defined actions using @capture("action"). Actions that are defined by
    # subclassing _AbstractAction do not use this class at all. This includes all built in actions and is also possible
    #  for user-defined actions.

    type: Literal["action"] = "action"
    # export_data and filter_interaction are here just so that legacy vm.Action(function=filter_interaction(...)) and
    # vm.Action(function=export_data(...)) work. They are always replaced with the new implementation by extracting
    # actions.function in _make_actions_chain. It's done as a forward ref here to avoid circular imports and resolved
    # with Dashboard.model_rebuild() later.
    function: Annotated[  # type: ignore[misc, assignment]
        SkipJsonSchema[Union[CapturedCallable, export_data, filter_interaction]],
        Field(json_schema_extra={"mode": "action", "import_path": "vizro.actions"}, description="Action function."),
    ]
    # inputs is deprecated and must only be used when _legacy = True. We don't use deprecated=True here because it only
    # affects the JSON schema and raises unwanted warnings when looking through model attributes. We use our own
    # make_deprecated_field_warning validator instead.
    # The type hint str here really means _IdOrIdProperty. We might change it in future for clearer API docs, but the
    # validation to check string format (presence of 0 or 1 . characters) does not need to be included in the
    # annotation. Options for good public API might be:
    # Union[ModelID, str] - where str refers to IdProperty, but ModelID is also str so this doesn't fully  make sense
    # Union[ModelID, IdProperty] - means making IdProperty public, which is ok but maybe overkill
    inputs: Annotated[
        list[str],
        Field(
            default=[],
            description="""List of inputs provided to the action function. Each input can be specified as
            `<model_id>` or `<model_id>.<argument_name>` or `<component_id>.<property>`. Defaults to `[]`.
            ❗Deprecated: `inputs` is deprecated and [will not exist in Vizro 0.2.0](
            deprecations.md#action-model-inputs-argument).""",
        ),
        BeforeValidator(
            make_deprecated_field_warning(
                "Pass references to runtime inputs directly as arguments of `function`. See "
                "https://vizro.readthedocs.io/en/stable/pages/API-reference/deprecations/#action-model-inputs-argument."
            )
        ),
    ]

    outputs: OutputsType  # type: ignore[misc]

    @property
    def _legacy(self) -> bool:
        if "inputs" in self.model_fields_set:
            # Deprecation warning has already been raised by make_deprecated_field_warning.
            legacy = True
        else:
            # If all supplied arguments look like states `<component_id>.<property>` or are model IDs then assume it's
            # a new type of action. For the case that there's no arguments and no inputs, this gives legacy=False.
            try:
                legacy = not all(
                    re.fullmatch("[^.]+[.][^.]+", arg_val) or arg_val in model_manager
                    for arg_val in self._runtime_args.values()
                )
            except TypeError:
                # arg_val isn't a string so it must be treated as a legacy action.
                legacy = True

            if legacy:
                warnings.warn(
                    "Passing a static argument to a custom action is deprecated and will not be possible in "
                    "Vizro 0.2.0. See https://vizro.readthedocs.io/en/stable/pages/API-reference/deprecations/static"
                    "-argument-for-custom-action.",
                    category=FutureWarning,
                )

        logger.debug("Action with id %s, function %s, has legacy=%s", self.id, self._action_name, legacy)
        return legacy

    _validate_function = field_validator("function", mode="before")(validate_captured_callable)

    @property
    def _parameters(self) -> set[str]:
        # TODO-AV2 B 2: in future, if we improve wrapping of __call__ inside CapturedCallable (e.g. by using wrapt),
        #  this could be done the same way as in _AbstractAction and avoid looking at _function. Then we could remove
        #  this _parameters property from both Action and _AbstractAction. Possibly also the _action_name one.
        #  Try and get IDE completion to work for action arguments.
        # Note order of parameters doesn't matter since we always handle things with keyword arguments.
        return set(inspect.signature(self.function._function).parameters)  # type:ignore[union-attr]

    @property
    def _runtime_args(self) -> dict[str, _IdOrIdProperty]:
        # Since function is a CapturedCallable, input arguments have already been bound and should be found from the
        # CapturedCallable.
        # Note this is a dictionary even if arguments were originally provided as positional ones, since they are
        # bound in CapturedCallable.
        # Currently, this does not use default values of function parameters. To do so, we would need to
        # use inspect.BoundArguments.apply_defaults.
        return self.function._arguments  # type:ignore[union-attr]

    @property
    def _action_name(self) -> str:
        return self.function._function.__name__  # type:ignore[union-attr]

    @property
    def _validated_outputs(self) -> OutputsType:
        # self.outputs has already been coerced to OutputsType so this is just an alias. We define it just so that
        # the interface of Action and _AbstractAction match.
        return self.outputs
