from __future__ import annotations

import abc
import inspect
from typing import Union

from dash import Output
from dash.development.base_component import Component
from pydantic import TypeAdapter

from vizro.models._action._action import _BaseAction
from vizro.models.types import _IdOrIdProperty


# TODO-AV2 D 5: make public.
class _AbstractAction(_BaseAction, abc.ABC):
    """`_AbstractAction` to be used in an `actions` field.

    To use this class, you must subclass it and define `function` and `outputs` to make a concrete action class. All
    built in actions follow this pattern, and it's also possible for user-defined actions. This class is not relevant
    for user-defined actions using `@capture("action")`.

    When subclassing, you can optionally define model fields. These can be either static or runtime arguments and
    define the configuration that a user specifies to use the action:

      * static arguments, e.g. `file_format = "csv"`, are fixed upfront and do not change depending on the state of the
      dashboard.
      * runtime arguments depend on the state of the running dashboard on the user's screen. These correspond to Dash
      States, e.g. `country="dropdown.value"` becomes `State("dropdown", "value")`.
    """

    # Note this model itself cannot have any fields (aside from `id` that comes from `VizroBaseModel`) or that field
    # would be inherited by all subclasses.

    @abc.abstractmethod
    def function(self, *args, **kwargs):
        """Function that must be defined by concrete action.

        This is always called using keyword-arguments so cannot have positional-only arguments.

        Any static arguments should not go explicitly in the function signature but instead be accessed through
        `self`, e.g. `self.file_format`.

        Any runtime arguments that were defined as model fields must go explicitly in the function signature,
        e.g. `country`.

        In addition to the runtime arguments specified as model fields, you can also use the following built-in
        arguments:

        * `_controls`: state of all the controls on the page. The format of is not yet decided and is likely to
        change in future versions.
        """
        pass

    @property
    @abc.abstractmethod
    def outputs(self) -> Union[list[_IdOrIdProperty], dict[str, _IdOrIdProperty]]:  # type: ignore[override]
        """Must be defined by concrete action, even if there's no output.

        This should return a dictionary of the form `{"key": "dropdown.value"}`, where the key corresponds to the key
        in the dictionary returned by the action `function`, and the value `"dropdown.value"` is converted into
        `Output("dropdown", "value", allow_duplicate=True)`.
        """
        # There should be no need to support dictionary IDs here. The only possible use is for pattern-matching IDs, but
        #  that will probably only be needed for built-in inputs. export_data currently overrides transformed_outputs to
        #  supply a dictionary ID but in future will probably change to use a single built-in vizro_download component.
        #  See https://github.com/mckinsey/vizro/pull/1054#discussion_r1989405177.
        #
        # We should probably not build in behavior here e.g. to generate outputs automatically from certain reserved
        # arguments since this would only work well for class-based actions and not @capture("action") ones. Instead
        # the code that does make_outputs_from_targets would be put into a reusable function.
        #
        # TODO-AV2 D 4: build in a vizro_download component. At some point after that consider changing export_data to
        #  use it, but that's not urgent. See  https://github.com/mckinsey/vizro/pull/1054#discussion_r1989405177.
        pass

    @property
    def _transformed_outputs(self) -> Union[list[Output], dict[str, Output]]:
        # Action.outputs is already validated by pydantic as list[str] or dict[str, str], but for
        # _AbstractAction.outputs we need to do the validation manually with TypeAdapter.
        TypeAdapter(Union[list[str], dict[str, str]]).validate_python(self.outputs)
        return super()._transformed_outputs

    @property
    def _dash_components(self) -> list[Component]:
        # This can be overridden in subclasses now but will probably not exist in future. Instead we will have built in
        # components like dcc.Download which are used by user-defined actions and (probably) built-in ones.
        # See https://github.com/mckinsey/vizro/pull/1054#discussion_r1989405177.
        return []

    @property
    def _legacy(self) -> bool:
        return False

    @property
    def _parameters(self) -> set[str]:
        # Note order of parameters doesn't matter since we always handle things with keyword arguments.
        return set(inspect.signature(self.function).parameters)

    @property
    def _runtime_args(self) -> dict[str, _IdOrIdProperty]:
        # Since function is not a CapturedCallable, input arguments have not yet been bound. They correspond to the
        # model fields that are present in the function signature. This is just the user-specified runtime arguments, as
        # static arguments are not in the function signature (they're in self) and built in runtime arguments are not
        # model fields. These will be of the form {"argument_name": "dropdown.value"}.
        return {
            arg_name: getattr(self, arg_name)
            for arg_name in self.__class__.model_fields
            if arg_name in self._parameters
        }

    @property
    def _action_name(self) -> str:
        return self.__class__.__name__
