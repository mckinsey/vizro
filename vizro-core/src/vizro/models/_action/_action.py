from __future__ import annotations

import inspect
import logging
import re
from collections.abc import Collection, Iterable, Mapping
from pprint import pformat
from typing import Annotated, Any, Literal, TypedDict, Union, cast

from dash import Input, Output, State, callback, html
from dash.development.base_component import Component
from pydantic import Field, StringConstraints, field_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.managers._model_manager import ModelID, model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable, ControlType, IdProperty, validate_captured_callable

logger = logging.getLogger(__name__)


class ControlsStates(TypedDict):
    filters: list[State]
    parameters: list[State]
    # TODO: filter_interaction won't be here in future.
    filter_interaction: list[dict[str, State]]


class _BaseAction(VizroBaseModel):
    def _get_control_states(self, control_type: ControlType) -> list[State]:
        """Gets list of `States` for selected `control_type` that appear on page where this Action is defined."""
        page = model_manager._get_model_page(self)
        return [
            State(component_id=control.selector.id, component_property=control.selector._input_property)
            for control in cast(Iterable[ControlType], model_manager._get_models(control_type, page))
        ]

    def _get_filter_interaction_states(self) -> list[dict[str, State]]:
        """Gets list of `States` for selected chart interaction `filter_interaction`."""
        from vizro.actions import filter_interaction
        from vizro.models._action._actions_chain import ActionsChain

        # TODO NOW: see if this logic can be simplified.

        def _get_action_trigger(action: _BaseAction) -> VizroBaseModel:  # type: ignore[return]
            """Gets the model that triggers the action with "action_id"."""
            # TODO NOW: maybe make model_manager._get_parent_model for this sort of thing. Maybe encode parent in id with
            #  dictionary id.

            for actions_chain in cast(Iterable[ActionsChain], model_manager._get_models(ActionsChain)):
                if action in actions_chain.actions:
                    return model_manager[ModelID(str(actions_chain.trigger.component_id))]

        page = model_manager._get_model_page(self)
        figure_interactions_on_page = model_manager._get_models(model_type=filter_interaction, page=page)
        states = []

        for action in figure_interactions_on_page:
            triggered_model = _get_action_trigger(action)
            required_attributes = ["_filter_interaction_input", "_filter_interaction"]
            for attribute in required_attributes:
                if not hasattr(triggered_model, attribute):
                    raise ValueError(f"Model {triggered_model.id} does not have required attribute `{attribute}`.")
            if "modelID" not in triggered_model._filter_interaction_input:
                raise ValueError(
                    f"Model {triggered_model.id} does not have required State `modelID` in `_filter_interaction_input`."
                )
            states.append(triggered_model._filter_interaction_input)

        return states

    @property
    def _transformed_inputs(self) -> Union[list[State], dict[str, Union[State, ControlsStates]]]:
        """Creates the actual Dash States given the user-specified runtime arguments and built in ones.

        Return type is list only for legacy actions. Otherwise it will always be a dictionary (unlike
        for _transformed_outputs, where new behaviour can still give a list). Keys are the parameter names. For
        user-specified inputs, values are Dash States. For built-in inputs, values can be more complicated nested
        structure of states.
        """
        if self._legacy:
            return [State(*input.split(".")) for input in self.inputs]

        from vizro.models import Filter, Parameter

        # TODO NOW: consider what else could be added, especially trigger.
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

        # TODO NOW: add some validation so this hits an error somewhere before this if can't do split. Bear
        #  in mind that in future it should work with just component name with no "."
        # User specified arguments runtime_args take precedence over built in reserved arguments. No static arguments
        # ar relevant here, just Dash States. Static arguments values are stored in the state of the relevant
        # AbstractAction instance.
        runtime_args = {arg_name: State(*arg_value.split(".")) for arg_name, arg_value in self._runtime_args.items()}

        return builtin_args | runtime_args

    @property
    def _transformed_outputs(self) -> Union[list[Output], dict[str, Output]]:
        """Creates the actual Dash Outputs based on self.outputs.

        Return type list[Output] is for legacy and new versions of Action. dict[str, Output] is for AbstractAction.
        """
        # TODO: enable both list and dict for both Action and AbstractAction.
        if isinstance(self.outputs, list):
            callback_outputs = [Output(*output.split("."), allow_duplicate=True) for output in self.outputs]

            # Need to use a single Output in the @callback decorator rather than a single element list for the case
            # of a single output. This means the action function can return a single value (e.g. "text") rather than a
            # single element list (e.g. ["text"]).
            if len(callback_outputs) == 1:
                callback_outputs = callback_outputs[0]
            return callback_outputs

        callback_outputs = {
            output_name: Output(*output.split("."), allow_duplicate=True)
            for output_name, output in self.outputs.items()
        }

        return callback_outputs

    @property
    def _dash_components(self) -> list[Component]:
        """Optional to override in subclasses of AbstractAction but defined here to keep interface same between
        Action and AbstractAction.

        This might not exist in future. TODO NOW COMMENT with link to github issue.
        """
        return []

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
            return_value = self.function(*inputs)
        else:
            return_value = self.function(**inputs)

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
        external_callback_inputs = self._transformed_inputs
        external_callback_outputs = self._transformed_outputs
        action_components = self._dash_components

        callback_inputs = {
            "external": external_callback_inputs,
            "internal": {"trigger": Input({"type": "action_trigger", "action_name": self.id}, "data")},
        }
        callback_outputs = {
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

        # TODO NOW: figure out where this belongs - in export_data? WHat other actions will have components? Does it
        #  matter where to put them on the page or they're all like Download?
        return html.Div(id=f"{self.id}_action_model_components_div", children=action_components, hidden=True)


class Action(_BaseAction):
    """Action to be inserted into `actions` of relevant component.

    This class is only relevant for user-defined actions using @capture("action"). Actions that are defined by
    subclassing AbstractAction do not use this class at all. This includes all built in actions and is also possible
    for user-defined actions.

    Args:
        function (CapturedCallable): Action function.
        inputs (list[str]): Inputs in the form `<component_id>.<property>` passed to the action function.
            Defaults to `[]`.
        outputs (list[str]): Outputs in the form `<component_id>.<property>` changed by the action function.
            Defaults to `[]`.
    """

    type: Literal["action"] = "action"
    # export_data and filter_interaction are here just so that legacy vm.Action(function=filter_interaction(...)) and
    # vm.Action(function=export_data(...)) work. They are always replaced with the new implementation by extracting
    # actions.function in _set_actions. It's done as a forward ref here to avoid circular imports and resolved with
    # Dashboard.model_rebuild() later.
    function: Annotated[
        SkipJsonSchema[Union[CapturedCallable, export_data, filter_interaction]],
        Field(json_schema_extra={"mode": "action", "import_path": "vizro.actions"}, description="Action function."),
    ]
    # inputs is a legacy field and will be deprecated. It must only be used when _legacy = True.
    # TODO: Put in deprecation warning.
    inputs: list[Annotated[str, StringConstraints(pattern="^[^.]+[.][^.]+$")]] = Field(
        [],
        description="Inputs in the form `<component_id>.<property>` passed to the action function.",
    )
    outputs: list[Annotated[str, StringConstraints(pattern="^[^.]+[.][^.]+$")]] = Field(
        [],
        description="Outputs in the form `<component_id>.<property>` changed by the action function.",
    )

    @property
    def _legacy(self) -> bool:
        # TODO: Put in deprecation warning.
        if "inputs" in self.model_fields_set:
            legacy = True
        else:
            # If all supplied arguments look like states `<component_id>.<property>` then assume it's a new type of
            # action. For the case that there's no arguments and no inputs, this gives legacy=False.
            legacy = not all(re.fullmatch("[^.]+[.][^.]+", arg_val) for arg_val in self._runtime_args.values())

        logger.debug("Action with id %s, function %s, has legacy=%s", self.id, self._action_name, legacy)
        return legacy

    _validate_function = field_validator("function", mode="before")(validate_captured_callable)

    @property
    def _parameters(self) -> set[str]:
        # TODO: in future, if we improve wrapping of __call__ inside CapturedCallable (e.g. by using wrapt),
        #  this could be done the same way as in AbstractAction and avoid looking at _function. Then we could remove
        #  this _parameters property from both Action and AbstractAction. Possibly also the _action_name one.
        # Note order of parameters doesn't matter since we always handle things with keyword arguments.
        return set(inspect.signature(self.function._function).parameters)

    @property
    def _runtime_args(self) -> dict[str, IdProperty]:
        # Since function is a CapturedCallable, input arguments have already been bound and should be found from the
        # CapturedCallable.
        # Note this is a dictionary even if arguments were originally provided as positional ones, since they are
        # bound in CapturedCallable.
        # Currently this does not use default values of function parameters. To do so, we would need to
        # use inspect.BoundArguments.apply_defaults.
        return self.function._arguments

    @property
    def _action_name(self):
        return self.function._function.__name__
