from __future__ import annotations

import inspect
import logging
from collections.abc import Collection, Mapping
from pprint import pformat
from typing import TYPE_CHECKING, Any, Callable, ClassVar, TypedDict, TypeVar, Union, get_args

from dash import Input, Output, State, callback, html
from dash.development.base_component import Component

from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID

try:
    from pydantic.v1 import Field, create_model, validator
except ImportError:  # pragma: no cov
    from pydantic import Field

from collections.abc import Iterable
from typing import cast

if TYPE_CHECKING:
    from vizro.models import Page
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable, ControlType

logger = logging.getLogger(__name__)


class Action(VizroBaseModel):
    """Action to be inserted into `actions` of relevant component.

    Args:
        function (CapturedCallable): Action function. See [`vizro.actions`][vizro.actions].
        inputs (list[str]): Inputs in the form `<component_id>.<property>` passed to the action function.
            Defaults to `[]`.
        outputs (list[str]): Outputs in the form `<component_id>.<property>` changed by the action function.
            Defaults to `[]`.

    """

    function: CapturedCallable = Field(..., import_path="vizro.actions", mode="action", description="Action function.")
    inputs: list[str] = Field(
        [],
        description="Inputs in the form `<component_id>.<property>` passed to the action function.",
        regex="^[^.]+[.][^.]+$",
    )
    outputs: list[str] = Field(
        [],
        description="Outputs in the form `<component_id>.<property>` changed by the action function.",
        regex="^[^.]+[.][^.]+$",
    )

    def _get_callback_mapping(self):
        """Builds callback inputs and outputs for the Action model callback, and returns action required components.

        callback_inputs, and callback_outputs are "dash.State" and "dash.Output" objects made of three parts:
            1. User configured inputs/outputs - for custom actions,
            2. Vizro configured inputs/outputs - for predefined actions,
            3. Hardcoded inputs/outputs - for custom and predefined actions
                (enable callbacks to live inside the Action loop).

        Returns: List of required components (e.g. dcc.Download) for the Action model added to the `Dashboard`
            container. Those components represent the return value of the Action build method.
        """
        # TODO NOW: comment this is only used by old actions.
        callback_inputs = [State(*input.split(".")) for input in self.inputs]
        callback_outputs = [Output(*output.split("."), allow_duplicate=True) for output in self.outputs]

        # Need to use a single Output in the @callback decorator rather than a single element list for the case
        # of a single output. This means the action function can return a single value (e.g. "text") rather than a
        # single element list (e.g. ["text"]).
        if len(callback_outputs) == 1:
            callback_outputs = callback_outputs[0]

        callback_components = []

        return callback_inputs, callback_outputs, callback_components

    def _action_callback_function(
        self,
        inputs: Union[dict[str, Any], list[Any]],
        outputs: Union[dict[str, Output], list[Output], Output, None],
    ) -> Any:
        logger.debug("===== Running action with id %s, function %s =====", self.id, self.function._function.__name__)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Action inputs:\n%s", pformat(inputs, depth=3, width=200))
            logger.debug("Action outputs:\n%s", pformat(outputs, width=200))

        if isinstance(inputs, Mapping):
            # TODO NOW: comment this is only NewAction
            return_value = self.function(**inputs)
        else:
            # TODO NOW: comment this is only old action
            return_value = self.function(*inputs)

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
        external_callback_inputs, external_callback_outputs, action_components = self._get_callback_mapping()
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
            self.function._function.__name__,
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


# TODO NOW: finish tidying/removing these helpers. Move into NewAction class as staticmethods.


def _get_inputs_of_controls(page: Page, control_type: ControlType) -> list[State]:
    """Gets list of `States` for selected `control_type` of triggered `Page`."""
    return [
        State(component_id=control.selector.id, component_property=control.selector._input_property)
        for control in cast(Iterable[ControlType], model_manager._get_models(control_type, page))
    ]


def _get_action_trigger(action: Action) -> VizroBaseModel:  # type: ignore[return]
    """Gets the model that triggers the action with "action_id"."""
    from vizro.models._action._actions_chain import ActionsChain
    # TODO: maybe make model_manager._get_parent_model for this sort of thing - see my shelf

    for actions_chain in cast(Iterable[ActionsChain], model_manager._get_models(ActionsChain)):
        if action in actions_chain.actions:
            return model_manager[ModelID(str(actions_chain.trigger.component_id))]


def _get_inputs_of_figure_interactions(page: Page, model_type: type[NewAction]) -> list[dict[str, State]]:
    """Gets list of `States` for selected chart interaction `filter_interaction` of triggered `Page`."""
    figure_interactions_on_page = model_manager._get_models(model_type=model_type, page=page)
    inputs = []
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
        inputs.append(triggered_model._filter_interaction_input)
    return inputs


class ControlInputs(TypedDict):
    filters: list[State]
    parameters: list[State]
    filter_interaction: list[dict[str, State]]

    # TODO NOW: figure out where this class lives


NOT_USED = object()


# can't subclass NewCustomAction since would then have outputs field which would need removing
class NewAction(VizroBaseModel):
    # can't define things like target here or won't get told if not available
    # just need to record somehwere to make sure it's only used when defined or to make private proxies of them like
    # _targets etc.
    # targets: Annotated[list[ModelID], "reserved"] = None
    # either two type hint or different sentinel value

    # just here to make filter_interacion etc. work, in reality should be instance and not class and use captured
    # callable
    function: ClassVar[Callable]

    # or just keep it as abstract staticmethod
    # should not be optional, just temporarily that before rewrite filter_interaction

    def _get_callback_mapping(self):
        """Builds callback inputs and outputs for the Action model callback, and returns action required components.

        callback_inputs, and callback_outputs are "dash.State" and "dash.Output" objects made of three parts:
            1. User configured inputs/outputs - for custom actions,
            2. Vizro configured inputs/outputs - for predefined actions,
            3. Hardcoded inputs/outputs - for custom and predefined actions
                (enable callbacks to live inside the Action loop).

        Returns: List of required components (e.g. dcc.Download) for the Action model added to the `Dashboard`
            container. Those components represent the return value of the Action build method.
        """
        return self.inputs, self.outputs, self.dash_components

    @property
    def outputs(self) -> dict[str, Output]:
        # TODO NOW: tidy and decide where this bit of code goes and how to get targets for filter and opl vs. parameter

        # TODO NOW: check if targets right type
        if hasattr(self, "targets"):
            targets = self.targets
        else:
            targets = []
        output_targets = []
        for target in targets:
            if "." in target:
                component, property = target.split(".", 1)
                output_targets.append(component)
            else:
                output_targets.append(target)

        return {
            target: Output(
                component_id=target,
                component_property=model_manager[target]._output_component_property,
                allow_duplicate=True,
            )
            for target in output_targets
        }

    @property
    def inputs(self) -> ControlInputs:
        from vizro.actions import filter_interaction
        from vizro.models import Filter, Parameter

        page = model_manager._get_model_page(self)

        # TODO NOW: create comment about refactoring ctds format in future. Comment that List[State] here would match
        #  custom actions.
        # TODO: consider names of these reserved arguments. vizro_filters? runtime_filters? __filters__? filters? Don't
        #  do using type
        #  hints - too complicated for user.
        # CHANGE TO TYPE HINTS OR vizro_ reserved words
        reserved_kwargs = {
            "filters": _get_inputs_of_controls(page=page, control_type=Filter),
            "parameters": _get_inputs_of_controls(page=page, control_type=Parameter),
            "filter_interaction": _get_inputs_of_figure_interactions(page=page, model_type=filter_interaction),
        }

        runtime_inputs = {}

        for key in inspect.signature(self.function).parameters:
            if key in reserved_kwargs:
                runtime_inputs[key] = reserved_kwargs[key]
            elif key in self.runtime_args:
                runtime_inputs[key] = State(*getattr(self, key).split("."))

        return runtime_inputs

    @property
    def dash_components(self) -> list[Component]:
        return []


NewAction.build = Action.build
NewAction._action_callback_function = Action._action_callback_function

# TODO NOW: doesn't seem to require Action to inherit from ABC, not sure why. Probably safest if we add it as
#  subclass anyway.
# Or try alternative approach where NewAction(Action) and then remove fields/methods.
Action.register(NewAction)


class NewCustomAction(VizroBaseModel):
    # note this is the same as Action so far but with inputs field different
    # only real enhancements are ability to inject filters etc. reserved arguments
    # and do inputs directly in function rather than as inputs argument
    # and possible new shorthand
    # could probably do as extension to existing class by populating inputs if not specified manually by matching
    # keyword arguments and splitting into State(*...)
    function: CapturedCallable = Field(..., import_path="vizro.actions", mode="action", description="Action function.")
    outputs: list[str]

    # all args are runtime states for now anyway - could add type hint for literals in future or just enable through
    # class only
    # hence no def runtime_args here
    # no dash_components possible here
    # c.f. NewAction
    @property
    def inputs(self) -> ControlInputs:
        from vizro.actions import filter_interaction
        from vizro.models import Filter, Parameter

        page = model_manager._get_model_page(self)

        # TODO NOW: create comment about refactoring ctds format in future. Comment that List[State] here would match
        #  custom actions.
        # TODO: consider names of these reserved arguments. vizro_filters? runtime_filters? __filters__? filters? Don't
        #  do using type
        #  hints - too complicated for user.
        # CHANGE TO TYPE HINTS OR vizro_ reserved words
        reserved_kwargs = {
            "filters": _get_inputs_of_controls(page=page, control_type=Filter),
            "parameters": _get_inputs_of_controls(page=page, control_type=Parameter),
            "filter_interaction": _get_inputs_of_figure_interactions(page=page, model_type=filter_interaction),
        }

        # assume all arguments are runtime arguments
        runtime_inputs = {}
        bound_args = {key: State(*value.split(".")) for key, value in self.function._arguments.items()}
        runtime_inputs |= bound_args
        runtime_inputs |= {
            key: value
            for key, value in reserved_kwargs.items()
            if key in inspect.signature(self.function._function).parameters
        }

        return runtime_inputs

    def _get_callback_mapping(self):
        """Builds callback inputs and outputs for the Action model callback, and returns action required components.

        callback_inputs, and callback_outputs are "dash.State" and "dash.Output" objects made of three parts:
            1. User configured inputs/outputs - for custom actions,
            2. Vizro configured inputs/outputs - for predefined actions,
            3. Hardcoded inputs/outputs - for custom and predefined actions
                (enable callbacks to live inside the Action loop).

        Returns: List of required components (e.g. dcc.Download) for the Action model added to the `Dashboard`
            container. Those components represent the return value of the Action build method.
        """
        # just same as current Action model for outputs
        outputs = [Output(*output.split(".")) for output in self.outputs]
        return self.inputs, outputs, self.dash_components

    # ALWAYS EMPTY for this sort of udf
    @property
    def dash_components(self) -> list[Component]:
        return []


Action.register(NewCustomAction)


NewCustomAction.build = Action.build
NewCustomAction._action_callback_function = Action._action_callback_function

VizroState = TypeVar("VizroState")
VizroOutput = TypeVar("VizroOutput")

if __name__ == "__main__":
    # Needs to work with default values too - need to parse these in NewCustomAction.
    def f(
        x: str,
        # targets: Annotated[str, "reserved"],
        # any_variable_name_but_expects_dropdown_value: VizroState,  # for people who care abotu type safety: Annotated[int, ""],
        # could also do as defeault value = State like in FastAPI old convention
        # for dropdown that gives int value
        # filters: Annotated[dict, Depends] = "filters",  # maybe dont need to provide default value or even type hint
    ):
        print("running function")
        print(f"{x=}")
        # print(f"{filters=}")

    f = capture_new_action2(f)
    1 / 0
    # f is capture_new_action2 type
    # f(x="a") -> gives NewCustomAction instance - correct

    # in config, user would do actions=[f(x="a")]
    # definitely don't provide filters
    # maybe fill out component_id_property_state
    # f(x="a", dropdown_value="dropdown_id.value") -> more reusable and attached to point of use. TRY THIS FIRST
    # how to distinguish x from dropdown_value? Would need special naming scheme or type hint. Don't like type hint
    # because obscures actual value provided and will break typing. Could do like FastAPI dependency injection? Looks
    # complicated for beginner though - don't like this.
    # Or dropdown_value=Wrapper("dropdown_id.value") - how to do through yaml? Could apply same scheme to filters etc. -
    # then no need for reserved arguments names, just would have default values like filters=Wrapper("filters").
    # So with this approach need either special argument name or special type provided or do e.g.
    # dropdown_value="vizro:**dropdown_id.value**".
    # Like Wrapper() best but how to do from JSON? Not sure. best is just to write Wrapper() as string like you would
    # do in python and then interpret that.
    # Only other options are special argument name or special argument value (but string).
    # Special argument value is better I think. Try "state:" for now and think of alternatives later.
    # Problem with string argument value is it breaks typing. Wrapper() is much better.
    # Use Annotated? Not simple to understand but correct way in FastAPI Depends.
    # Using type hint will also break typing unless do as annotated.
    # Best options now are special argument name - but this also breaks typing!!
    # Overall best option is like FastAPI Depends.
    # OR
    # f(x="a")
    # and hardcode component into function signature -> less complex - still needs special argument name or type hint.
    # Don't want to do type hint.
    # OR ENABLE BOTH?
    # even better to just provide component_id and then it guesses property if not supplied

    # OR don't allow static arguments for custom callbacks - instead need to define full pydantic class or make
    # function factory? So all arguments are Dash inputs. This is the case in Dash and seems ok there.
    # Could enable special static arguments if required using one of the above ideas - make them the ones which are
    # harder to do since they're less common.
    # Type hint shouldn't be needed for detection of Dash input but ideally would be possible to do type annotations
    # nicely somehow e.g. Annotated. Or custom action decorator changes type hints on the fly.
    # Don't worry about typing currently, just interpret all arguments as states and fix trigger with parent
    # component. SOUNDS LIKE GOOD IDEA.
    f(x=2, any_variable_name_but_expects_dropdown_value="state:dropdown_id.value").function()
    # LATEST THINKING:
    # Interpret all arguments as states, don't worry about literal ones (Dash doesn't) but could make it work with
    # type hint in future
    # Do type hint match and name match on reserved args including output.
    # Would defined on Vizro side Targets = Annotated[str, "RESERVED"] or similar.

# T = TypeVar('T')
# Const = Annotated[T, my_annotations.CONST]
#
# class C:
#     def const_method(self: Const[List[int]]) -> int:
#         ...
# should only need to use type hint if you actually care about type safety
