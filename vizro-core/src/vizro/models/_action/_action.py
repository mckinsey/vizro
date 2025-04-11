from __future__ import annotations

import inspect
import logging
import re
from collections.abc import Collection, Iterable, Mapping
from pprint import pformat
from typing import TYPE_CHECKING, Annotated, Any, Callable, ClassVar, Literal, Union, cast

from dash import Input, Output, State, callback, html
from dash.development.base_component import Component
from pydantic import Field, StringConstraints, TypeAdapter, ValidationError, field_validator
from pydantic.json_schema import SkipJsonSchema
from typing_extensions import TypedDict

from vizro.managers._model_manager import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable, ControlType, _IdProperty, validate_captured_callable

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
    outputs: ClassVar[Union[list[_IdProperty], dict[str, _IdProperty]]]

    @property
    def _dash_components(self) -> list[Component]:
        raise NotImplementedError

    @property
    def _legacy(self):
        raise NotImplementedError

    @property
    def _parameters(self) -> set[str]:
        raise NotImplementedError

    @property
    def _runtime_args(self) -> dict[str, _IdProperty]:
        raise NotImplementedError

    @property
    def _action_name(self) -> str:
        raise NotImplementedError

    def _validate_dash_dependencies(self, /, dependencies, *, type: Literal["output", "input"]):
        # Validate that dependencies are in the form component_id.component_property. This uses the same annotation as
        # Action.inputs/outputs.
        # TODO-AV2 D 2: in future we will expand this to also allow passing a model name without a property specified,
        #  so long as _output_component_property exists - need to handle case it doesn't with error.
        #  Possibly make a built in a type hint that we can use as field annotation for runtime arguments in
        #  subclasses of _AbstractAction instead of just using str. Possibly apply this to non-annotated arguments of
        #  vm.Action.function and use pydantic's validate_call to apply the same validation there for function inputs.
        #  We won't be able to do all the checks at validation time though if we need to look up a model in the model
        #  manager. When this change is made the outputs property for filter, parameter and on_page_load should just
        #  become `return self.targets` or similar. Consider again whether to do this translation automatically if
        #  targets is defined as a field, but sounds like bad idea since it doesn't carry over into the
        #  capture("action") style of action.
        # TODO-AV D 3: try to enable properties that aren't Dash properties but are instead model fields e.g. header,
        #  title. See https://github.com/mckinsey/vizro/issues/1078.
        #  Note this is needed for inputs in both vm.Action and _AbstractAction but outputs only in _AbstractAction.
        try:
            TypeAdapter(list[Annotated[str, StringConstraints(pattern="^[^.]+[.][^.]+$")]]).validate_python(
                dependencies
            )
        except ValidationError as exc:
            invalid_dependencies = {
                error["input"] for error in exc.errors() if error["type"] == "string_pattern_mismatch"
            }
            raise ValueError(
                f"Action {type}s {invalid_dependencies} of {self._action_name} must be a string of the form "
                "<component_name>.<component_property>."
            ) from exc

    def _get_control_states(self, control_type: ControlType) -> list[State]:
        """Gets list of `States` for selected `control_type` that appear on page where this Action is defined."""
        # Possibly the code that specifies the state associated with a control will move to an inputs property
        # of the filter and parameter models in future. This property could match outputs and return just a dotted
        # string that is then transformed to State inside _transformed_inputs. This would prevent us from using
        # pattern-matching callback here though.
        # See also notes in filter_interaction._get_triggered_model.
        page = model_manager._get_model_page(self)
        return [
            State(component_id=control.selector.id, component_property=control.selector._input_property)
            for control in cast(Iterable[ControlType], model_manager._get_models(control_type, page))
        ]

    def _get_filter_interaction_states(self) -> list[dict[str, State]]:
        """Gets list of `States` for selected chart interaction `filter_interaction`."""
        from vizro.actions import filter_interaction

        page = model_manager._get_model_page(self)
        return [
            action._get_triggered_model()._filter_interaction_input
            for action in model_manager._get_models(filter_interaction, page=page)
        ]

    @property
    def _transformed_inputs(self) -> Union[list[State], dict[str, Union[State, ControlsStates]]]:
        """Creates the actual Dash States given the user-specified runtime arguments and built in ones.

        Return type is list only for legacy actions. Otherwise it will always be a dictionary (unlike
        for _transformed_outputs, where new behavior can still give a list). Keys are the parameter names. For
        user-specified inputs, values are Dash States. For built-in inputs, values can be more complicated nested
        structure of states.
        """
        if self._legacy:
            # Must be an Action rather than _AbstractAction, so has already been validated by pydantic field annotation.
            return [State(*input.split(".")) for input in cast(Action, self).inputs]

        from vizro.models import Filter, Parameter

        builtin_args = {
            "_controls": {
                "filters": self._get_control_states(control_type=Filter),
                "parameters": self._get_control_states(control_type=Parameter),
                "filter_interaction": self._get_filter_interaction_states(),
            }
        }

        # Work out which built in arguments are actually required for this function.
        builtin_args = {
            arg_name: arg_value for arg_name, arg_value in builtin_args.items() if arg_name in self._parameters
        }

        # Validate that the runtime arguments are in the same form as the legacy Action.inputs field, so a string
        # of the form component_id.component_property. Currently this code only runs for subclasses of
        # _AbstractAction but not vm.Action instances because a vm.Action that does not pass this check will
        # have already been classified as legacy in Action._legacy. In future when vm.Action.inputs is deprecated
        # then this will be used for vm.Action instances also.
        self._validate_dash_dependencies(self._runtime_args.values(), type="input")

        # User specified arguments runtime_args take precedence over built in reserved arguments. No static arguments
        # ar relevant here, just Dash States. Static arguments values are stored in the state of the relevant
        # _AbstractAction instance.
        runtime_args = {arg_name: State(*arg_value.split(".")) for arg_name, arg_value in self._runtime_args.items()}

        return builtin_args | runtime_args

    @property
    def _transformed_outputs(self) -> Union[list[Output], dict[str, Output]]:
        """Creates the actual Dash Outputs based on self.outputs.

        Legacy and new versions of Action just support list[Output]. _AbstractAction subclasses support
        dict[str, Output] and list[Output].
        """
        # TODO-AV2 D 1: enable dict for Action. Also think about where all the validation in this function should go
        #  since it's only relevant for _AbstractAction because vm.Action models have pydantic validation built into the
        #  field annotation.
        if isinstance(self.outputs, list):
            self._validate_dash_dependencies(self.outputs, type="output")
            callback_outputs = [Output(*output.split("."), allow_duplicate=True) for output in self.outputs]

            # Need to use a single Output in the @callback decorator rather than a single element list for the case
            # of a single output. This means the action function can return a single value (e.g. "text") rather than a
            # single element list (e.g. ["text"]).
            if len(callback_outputs) == 1:
                callback_outputs = callback_outputs[0]
            return callback_outputs

        self._validate_dash_dependencies(self.outputs.values(), type="output")
        callback_outputs = {  # type: ignore[assignment]
            output_name: Output(*output.split("."), allow_duplicate=True)
            for output_name, output in self.outputs.items()
        }

        return callback_outputs

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
    def build(self) -> html.Div:
        """Builds a callback for the Action model and returns required components for the callback.

        Returns:
            Div containing a list of required components (e.g. dcc.Download) for the Action model

        """
        # TODO: after sorting out model manager and pre-build order, lots of this should probably move to happen
        #  some time before the build phase.
        external_callback_inputs = self._transformed_inputs
        external_callback_outputs = self._transformed_outputs

        callback_inputs = {
            "external": external_callback_inputs,
            "internal": {"trigger": Input({"type": "action_trigger", "action_name": self.id}, "data")},
        }
        callback_outputs: dict[str, Union[list[Output], dict[str, Output]]] = {
            "internal": {"action_finished": Output("action_finished", "data", allow_duplicate=True)},
        }

        # If there are no outputs then we don't want the external part of callback_outputs to exist at all.
        # This allows the action function to return None and match correctly on to the callback_outputs dictionary
        # The (probably better) alternative to this would be just to define a dummy output for all such functions
        # so that the external key always exists.
        # Note that it's still possible to explicitly return None as a value when an output is specified.
        if external_callback_outputs:
            callback_outputs["external"] = external_callback_outputs

        logger.debug(
            "===== Building callback for Action with id %s, function %s =====",
            self.id,
            self._action_name,
        )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Callback inputs:\n%s", pformat(callback_inputs["external"], width=200))
            logger.debug("Callback outputs:\n%s", pformat(callback_outputs.get("external"), width=200))

        @callback(output=callback_outputs, inputs=callback_inputs, prevent_initial_call=True)
        def callback_wrapper(external: Union[list[Any], dict[str, Any]], internal: dict[str, Any]) -> dict[str, Any]:
            return_value = self._action_callback_function(inputs=external, outputs=callback_outputs.get("external"))
            if "external" in callback_outputs:
                return {"internal": {"action_finished": None}, "external": return_value}
            return {"internal": {"action_finished": None}}

        return html.Div(id=f"{self.id}_action_model_components_div", children=self._dash_components, hidden=True)


class Action(_BaseAction):
    """Action to be inserted into `actions` of relevant component.

    Args:
        function (CapturedCallable): Action function.
        inputs (list[str]): Inputs in the form `<component_id>.<property>` passed to the action function.
            Defaults to `[]`.
        outputs (list[str]): Outputs in the form `<component_id>.<property>` changed by the action function.
            Defaults to `[]`.
    """

    # TODO-AV2 D 5: when it's made public, add something like below to docstring:
    # This class is only relevant for user-defined actions using @capture("action"). Actions that are defined by
    # subclassing _AbstractAction do not use this class at all. This includes all built in actions and is also possible
    #  for user-defined actions.

    type: Literal["action"] = "action"
    # export_data and filter_interaction are here just so that legacy vm.Action(function=filter_interaction(...)) and
    # vm.Action(function=export_data(...)) work. They are always replaced with the new implementation by extracting
    # actions.function in _set_actions. It's done as a forward ref here to avoid circular imports and resolved with
    # Dashboard.model_rebuild() later.
    # TODO-AV2 C 1: Need to think about which parts of validation in CapturedCallable are legacy and how user
    # now specifies a user defined action in YAML (ok if not possible initially since it's not already) - could just
    # enable class-based one? Presumably import_path is no longer relevant though.
    function: Annotated[  # type: ignore[misc, assignment]
        SkipJsonSchema[Union[CapturedCallable, export_data, filter_interaction]],
        Field(json_schema_extra={"mode": "action", "import_path": "vizro.actions"}, description="Action function."),
    ]
    # inputs is a legacy field and will be deprecated. It must only be used when _legacy = True.
    # TODO-AV2 C 1: Put in deprecation warning.
    inputs: list[Annotated[str, StringConstraints(pattern="^[^.]+[.][^.]+$")]] = Field(
        [],
        description="Inputs in the form `<component_id>.<property>` passed to the action function.",
    )
    outputs: list[Annotated[str, StringConstraints(pattern="^[^.]+[.][^.]+$")]] = Field(  # type: ignore
        [],
        description="Outputs in the form `<component_id>.<property>` changed by the action function.",
    )

    @property
    def _dash_components(self) -> list[Component]:
        # Users cannot add Dash components using vm.Action.
        return []

    @property
    def _legacy(self) -> bool:
        # TODO-AV2 C 1: add deprecation warnings

        if "inputs" in self.model_fields_set:
            legacy = True
        else:
            # If all supplied arguments look like states `<component_id>.<property>` then assume it's a new type of
            # action. For the case that there's no arguments and no inputs, this gives legacy=False.
            try:
                legacy = not all(re.fullmatch("[^.]+[.][^.]+", arg_val) for arg_val in self._runtime_args.values())
            except TypeError:
                # arg_val isn't a string so it must be treated as a legacy action.
                legacy = True

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
    def _runtime_args(self) -> dict[str, _IdProperty]:
        # Since function is a CapturedCallable, input arguments have already been bound and should be found from the
        # CapturedCallable.
        # Note this is a dictionary even if arguments were originally provided as positional ones, since they are
        # bound in CapturedCallable.
        # Currently this does not use default values of function parameters. To do so, we would need to
        # use inspect.BoundArguments.apply_defaults.
        return self.function._arguments  # type:ignore[union-attr]

    @property
    def _action_name(self) -> str:
        return self.function._function.__name__  # type:ignore[union-attr]
