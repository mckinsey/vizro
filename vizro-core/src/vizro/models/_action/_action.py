from __future__ import annotations

import inspect
import logging
from abc import abstractmethod
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
    from pydantic import Field, PrivateAttr

from collections.abc import Iterable
from typing import cast

if TYPE_CHECKING:
    from vizro.models import Page
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable, ControlType, capture

logger = logging.getLogger(__name__)


# NO LONGER NEEDS TO HANDLE BUILT-IN ACTIONS
# will continue to be called Action in future?
class Action(VizroBaseModel):
    # note this is the same as Action so far but with inputs field different
    # only real enhancements are ability to inject filters etc. reserved arguments
    # and do inputs directly in function rather than as inputs argument
    # and possible new shorthand

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
    )  # legacy only
    outputs: list[str] = Field(
        [],
        description="Outputs in the form `<component_id>.<property>` changed by the action function.",
        regex="^[^.]+[.][^.]+$",
    )

    # SET WITH validator and make private
    legacy: bool = False

    @property
    def _function_(self) -> CapturedCallable:
        return self.function

    # shouldn't really exist here
    @property
    def dash_components(self):
        return []

    # in fact doesn't need to be property at all, just helpe function inside Action and AbstractionAction
    @property
    def _inputs_(self) -> ControlInputs:
        if self.legacy:
            return [State(*input.split(".")) for input in self.inputs]

        from vizro.actions import filter_interaction
        from vizro.models import Filter, Parameter

        page = model_manager._get_model_page(self)

        # TODO NOW: create comment about refactoring ctds format in future. Comment that List[State] here would match
        #  custom actions.
        # TODO: consider names of these reserved arguments. vizro_filters? runtime_filters? __filters__? filters? Don't
        #  do using type
        #  hints - too complicated for user.
        reserved_kwargs = {
            "filters": _get_inputs_of_controls(page=page, control_type=Filter),
            "parameters": _get_inputs_of_controls(page=page, control_type=Parameter),
            "filter_interaction": _get_inputs_of_figure_interactions(page=page, model_type=filter_interaction),
        }

        #     # all args are runtime states for now anyway - could add type hint for literals in future or just enable through
        #     # class implementation only
        runtime_inputs = {}
        # excludes self and hence all static args
        # if user has used reserved_kwargs then give user preference over built-in
        # this keeps it future-proof for adding new reserved kwargs with no need for vizro_ prefix or type hint
        for key in inspect.signature(self._function_._function).parameters:  # all arguments
            if key in reserved_kwargs and key not in self._function_._arguments:  # bound arguments
                runtime_inputs[key] = reserved_kwargs[key]
            else:
                runtime_inputs[key] = State(*self._function_[key].split("."))

        return runtime_inputs

    # similarly doesn't need to be property, just some helper function that manipulates self.outputs to give actual
    # outputs
    @property
    def _outputs_(self):
        # MAKE PROPER HELPER FUNCTION THAT GOES THROUGH LIST/DICT/ETC. of dotted strings and converts to Output
        # legacy and new behaviour is same
        if isinstance(self.outputs, list):
            callback_outputs = [Output(*output.split("."), allow_duplicate=True) for output in self.outputs]

            # Need to use a single Output in the @callback decorator rather than a single element list for the case
            # of a single output. This means the action function can return a single value (e.g. "text") rather than a
            # single element list (e.g. ["text"]).
            if len(callback_outputs) == 1:
                callback_outputs = callback_outputs[0]

            return callback_outputs

        # else it's a mapping - means AbstractAction but in future also Action
        callback_outputs = {
            output_name: Output(*output.split("."), allow_duplicate=True)
            for output_name, output in self.outputs.items()
        }
        # WHAT ABOUT NO OUTPUTS?
        return callback_outputs

    def _action_callback_function(
        self,
        inputs: Union[dict[str, Any], list[Any]],
        outputs: Union[dict[str, Output], list[Output], Output, None],
    ) -> Any:
        logger.debug("===== Running action with id %s, function %s =====", self.id, self._function_._function.__name__)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Action inputs:\n%s", pformat(inputs, depth=3, width=200))
            logger.debug("Action outputs:\n%s", pformat(outputs, width=200))

        if self.legacy:
            # only relevant for Action model
            return_value = self._function_(*inputs)
        else:
            # this is AbstrAction and new behaviour in Action
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
        action_components = [] if self.legacy else self.dash_components

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


# TODO NOW: finish tidying/removing these helpers. Move into AbstractAction class as staticmethods.


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


def _get_inputs_of_figure_interactions(page: Page, model_type: type[AbstractAction]) -> list[dict[str, State]]:
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


# All built in actions and user can also do this if wanted
class AbstractAction(VizroBaseModel):
    legacy = False

    # implementation dependent, can't go in schema. Prefix with vizro_ or _ or similar to avoid clash on subclassing?
    # maybe a subclass hook can prevent this already?
    # RUN TIME FUNCTION
    # not classvar actually if captured callable since depends on this instance's inputs
    # Must be set using property or as private attribute assigned using validator or default factory.
    @property
    def _function_(self) -> CapturedCallable:
        # only need runtime args that aren't reserved
        # static args go through self
        # CHECK THIS LOGIC - should work same way for user-defined filter overriding built in
        inputs = {
            key: getattr(self, key) for key in set(inspect.signature(self.function).parameters) & set(self.__fields__)
        }
        return capture("action")(self.function)(**inputs)

    # @abstractmethod - yes
    # keyword args only?
    # user writes this
    def function(self):
        pass

    # optional
    # maybe some automatic "convert from targets" etc. function would go in here in the future some time
    # allows same as Action.outputs but maybe in future will also allow dictionary outputs instead of needing to
    # override _outputs_ for that
    # even if add more funcitonality here in future shoulod still support same as Action.output: list[str] so it's
    # easy for someone to write a class action isntead of function one
    # WILL ALWAYS NEED TO SUPPORT STRING FOR WHEN DON'T SUPPLY X.Y BUT INSTEAD X
    @property
    def outputs(self) -> dict[str, str]:
        return dict()

    # optional
    @property
    def dash_components(self) -> dict[str, Output]:
        return dict()


AbstractAction.build = Action.build
AbstractAction._action_callback_function = Action._action_callback_function
AbstractAction._inputs_ = Action._inputs_
AbstractAction._outputs_ = Action._outputs_

# TODO NOW: doesn't seem to require Action to inherit from ABC, not sure why. Probably safest if we add it as
#  subclass anyway.
# Or try alternative approach where AbstractAction(Action) and then remove fields/methods.
Action.register(AbstractAction)

VizroState = TypeVar("VizroState")
VizroOutput = TypeVar("VizroOutput")

if __name__ == "__main__":
    # Needs to work with default values too - need to parse these in Action.
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
    # f(x="a") -> gives Action instance - correct

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
