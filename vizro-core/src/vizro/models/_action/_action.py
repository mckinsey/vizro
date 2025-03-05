from __future__ import annotations

import inspect
import logging
import re
from collections.abc import Collection, Iterable, Mapping
from pprint import pformat
from typing import Annotated, Any, NewType, TypedDict, Union, cast

from dash import Input, Output, State, callback, html
from dash.development.base_component import Component
from pydantic import Field, StringConstraints, field_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.managers._model_manager import ModelID, model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable, ControlType, capture, validate_captured_callable

logger = logging.getLogger(__name__)

# TODO NOW: work out where these definitions go and if they're a good idea.
# For "component_id.component_property", e.g. "dropdown_id.value".
IdProperty = NewType("IdProperty", str)


# TODO NOW: check actual structure of this. Does it use IdProperty?
# TODO FUTURE: improve structure. Needs pattern mathcing?
class Controls(TypedDict):
    filters: list[Any]
    parameters: list[Any]
    # TODO: filter_interaction won't be here in future.
    filter_interaction: list[dict[str, Any]]


class ControlsState(TypedDict):
    filters: list[State]
    parameters: list[State]
    filter_interaction: list[dict[str, State]]


class Action(VizroBaseModel):
    """Action to be inserted into `actions` of relevant component.

    Args:
        function (CapturedCallable): Action function.
        inputs (list[str]): Inputs in the form `<component_id>.<property>` passed to the action function.
            Defaults to `[]`.
        outputs (list[str]): Outputs in the form `<component_id>.<property>` changed by the action function.
            Defaults to `[]`.

    TODO NOW COMMENT: only needed for custom actions.
    """

    # export_data and filter_interaction are here just so that legacy vm.Action(function=filter_interaction(...)) and
    # vm.Action(function=export_data(...)) work. It's done as a forward ref to avoid circular imports and resolved with
    # Action.model_rebuild() later.
    function: Annotated[
        SkipJsonSchema[Union[CapturedCallable, export_data, filter_interaction]],
        Field(json_schema_extra={"mode": "action", "import_path": "vizro.actions"}, description="Action function."),
    ]
    # This is a legacy field and will be deprecated. It must only be used when _legacy = True.
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
        # This is only relevant for custom actions, not built in. All built in ones are always legacy = False.
        # TODO NOW: take out debugging print and put back early returns
        if "inputs" in self.model_fields_set:
            legacy = True
        else:
            # If all supplied arguments look like states `<component_id>.<property>` then assume it's a new type of action.
            # For the case that there's no arguments and no inputs, this gives legacy=False.
            legacy = not all(re.fullmatch("[^.]+[.][^.]+", arg_val) for arg_val in self.function._arguments.values())
        print(f"{self.function} {legacy=}")
        return legacy

    _validate_function = field_validator("function", mode="before")(validate_captured_callable)

    @property
    def _function_(self) -> CapturedCallable:
        # TODO NOW COMMENT
        return self.function

    @property
    def dash_components(self):
        # TODO NOW COMMENT
        return []

    @property
    def _inputs_(self) -> dict[str, Any]:
        # TODO NOW: figure out return type, how nested it can be, how to match custom action inputs
        # TODO NOW COMMENT
        if self._legacy:
            return [State(*input.split(".")) for input in self.inputs]

        from vizro.models import Filter, Parameter

        # TODO NOW: consider what else could be added, especially trigger.
        builtin_args = {
            "controls": {
                "filters": self._get_control_states(control_type=Filter),
                "parameters": self._get_control_states(control_type=Parameter),
                "filter_interaction": self._get_filter_interaction_states(),
            }
        }

        # Fetch all runtime arguments, both user-specified and built in ones. User specified arguments take precedence
        # over built in reserved arguments. Static arguments are excluded
        runtime_args = {}
        # TODO NOW: look again at captured callable for how to handle _function etc. Maybe if used wrapt it would be
        #  nicer?
        # TODO NOW: check below statemtn and test overriding works as expected
        # The signature parameters don't include self and hence all static arguments are excluded.
        for arg_name in inspect.signature(self._function_._function).parameters:
            # If the argument name is a builtin one and hasn't already been bound then take it from the built ins.
            # Otherwise, interpret the value given as a state.
            if arg_name in builtin_args and arg_name not in self._function_._arguments:
                runtime_args[arg_name] = builtin_args[arg_name]
            else:
                # TODO NOW: add some validation so this hits an error somewhere before this if can't do split. Bear
                #  in mind that in future it should work with just component name with no "."
                runtime_args[arg_name] = State(*self._function_[arg_name].split("."))

        return runtime_args

    def _get_control_states(self, control_type: ControlType) -> list[State]:
        """Gets list of `States` for selected `control_type` that appear on page where this Action is defined."""
        page = model_manager._get_model_page(self)
        return [
            State(component_id=control.selector.id, component_property=control.selector._input_property)
            for control in cast(Iterable[ControlType], model_manager._get_models(control_type, page))
        ]

    def _get_filter_interaction_states(self) -> list[dict[str, State]]:
        """Gets list of `States` for selected chart interaction `filter_interaction` of triggered `Page`."""
        from vizro.actions import filter_interaction
        from vizro.models._action._actions_chain import ActionsChain

        # TODO NOW: see if this logic can be simplified.

        def _get_action_trigger(action: Action) -> VizroBaseModel:  # type: ignore[return]
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
    def _outputs_(
        self,
    ) -> Union[list[Output], dict[str, Output]]:
        # TODO NOW COMMENT
        # list[Output] is relevant for both legacy and new versions.
        # dict[str, Output] is currently only possible with AbstractAction but should be possible in future also with
        # Action.
        # In general we might want to handle more general structures than this for both input and output.
        # TODO NOW: make proper helper function that goes through nested list/dict/etc. of dotted strings and converts
        #  to Output. Is it also relevant for inputs? These should always be built in (for complex cases), in which
        #  case no need to work with strings (e.g. if use pattern matching) or just a single string. Might want to
        #  allow list[str] even for inputs though? Think about this.
        # Action case (either legacy or new):
        if isinstance(self.outputs, list):
            callback_outputs = [Output(*output.split("."), allow_duplicate=True) for output in self.outputs]

            # Need to use a single Output in the @callback decorator rather than a single element list for the case
            # of a single output. This means the action function can return a single value (e.g. "text") rather than a
            # single element list (e.g. ["text"]).
            # TODO NOW: check this is the best way to do this.
            if len(callback_outputs) == 1:
                callback_outputs = callback_outputs[0]
            return callback_outputs

        # AbstractAction case:
        callback_outputs = {
            output_name: Output(*output.split("."), allow_duplicate=True)
            for output_name, output in self.outputs.items()
        }
        # TODO NOW: check what happens if no outputs?
        return callback_outputs

    def _action_callback_function(
        self,
        inputs: Union[dict[str, Any], list[Any]],
        outputs: Union[dict[str, Output], list[Output], Output, None],
    ) -> Any:
        # TODO NOW: check how this works.
        logger.debug("===== Running action with id %s, function %s =====", self.id, self._function_._function.__name__)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Action inputs:\n%s", pformat(inputs, depth=3, width=200))
            logger.debug("Action outputs:\n%s", pformat(outputs, width=200))

        if self._legacy:
            # Inputs must be list[str].
            return_value = self._function_(*inputs)
        else:
            # TODO NOW: check this:
            # even if user supplies positional arguments (if remains to be possible), captured callable will handle
            # it to bind to kwargs
            return_value = self._function_(**inputs)

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
        external_callback_inputs = self._inputs_
        external_callback_outputs = self._outputs_
        action_components = [] if self._legacy else self.dash_components

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
            self._function_._function.__name__,
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


# TODO NOW: work out relationship of this to Action.
class AbstractAction(VizroBaseModel):
    # TODO NOW COMMENT: All built in actions and user can also do this if wanted
    _legacy = False

    # TODO NOW COMMENT: Check schema and make sure these don't appear, comment on importance of this.

    @property
    def _function_(self) -> CapturedCallable:
        # Capture just runtime arguments that aren't reserved. Static argument go through self and built in runtime
        # arguments are not known upfront. Hence look at arguments that are model fields and explicitly in the
        # function signature. This also excludes fields like id that have been inherited from VizroBaseModel.
        arg_names = set(self.model_fields) & set(inspect.signature(self.function).parameters)
        captured_callable = capture("action")(self.function)
        return captured_callable(**{arg_name: getattr(self, arg_name) for arg_name in arg_names})

    # TODO NOW: work out if should be @abstractmethod. Or maybe use decorator instead of function/_function_ relationship here.
    # TODO NOW: make keyword args only? What are actual limitations here? Don't worry much about it.
    def function(self, *args, **kwargs):
        """Function that must be defined by concrete action.

        Can use:
          - static arguments: model fields, not explicitly in function signature, go through self. Uses self and not
            Dash State
          - runtime arguments: model fields, explicitly in function signature. Uses Dash State
          - built in runtime arguments: not model fields, explicitly in function signature. Uses Dash State
        """
        raise NotImplementedError

    @property
    def outputs(self) -> dict[str, IdProperty]:
        """Optional to override."""
        # TODO NOW OR IN FUTURE: handle list[str], align with Action. Maybe allow more deeply nested things too.
        # TODO NOW: should it handle dictionary ids too? Currently this needs overriding _outputs_. Pattern matching
        # probably not needed for outputs and only for built-in inputs. Even if add more functionality here in future
        # we shoulod still at least the support same as Action.output so it's easy for someone to move from a function
        # action to a class one. In future we'd even like to just allow specifying the component id without the property.

        # Maybe there will be some special built-in behaviour here e.g. to generate outputs automatically from
        # certain reserved arguments like self.targets. Would need to make sure it's not breaking if someone already
        # uses that variable name though.
        return dict()

    @property
    def dash_components(self) -> dict[str, Component]:
        """Optional to override."""
        # TODO NOW: is it a dict?
        return dict()


# TODO NOW: figure out correct structure to avoid doing this. Note _validate function shouldn't be inherited.
AbstractAction._get_control_states = Action._get_control_states
AbstractAction._get_filter_interaction_states = Action._get_filter_interaction_states
AbstractAction._inputs_ = Action._inputs_
AbstractAction._outputs_ = Action._outputs_
AbstractAction._action_callback_function = Action._action_callback_function
AbstractAction.build = Action.build
Action.register(AbstractAction)
