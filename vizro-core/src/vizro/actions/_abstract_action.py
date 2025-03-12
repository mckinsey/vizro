from __future__ import annotations

import abc
import inspect

from vizro.models._action._action import IdProperty, _BaseAction


class AbstractAction(_BaseAction, abc.ABC):
    """AbstractAction to be inserted into `actions` of relevant component.

    To use this class, you must subclass it and define `function` and `outputs` to make a concrete action class. All
    built in actions follow this pattern, and it's also an option for user-defined acftions. This class is not
    relevant for user-defined actions using @capture("action").

    When subclassing, you can optionally define model fields. The handling of fields depends on whether it is also
    present in the function signature:
      - static arguments, e.g. file_format = "csv": model fields, not explicitly in function signature, go through self.
        Uses self and not Dash State
      - runtime arguments, e.g. arg_name="dropdown.value": model fields, explicitly in function signature. Uses Dash
        State
      - built in runtime arguments, e.g. controls: not model fields, explicitly in function signature. Uses Dash State
    """

    _legacy = False

    # TODO NOW COMMENT: Check schema and make sure these don't appear, comment on importance of this.

    # TODO NOW: make keyword args only? What are actual limitations here? Don't worry much about it.
    @abc.abstractmethod
    def function(self, *args, **kwargs):
        """Function that must be defined by concrete action."""
        pass

    @property
    @abc.abstractmethod
    def outputs(self) -> dict[str, IdProperty]:
        """Must be defined by concrete action, even if there's no output."""
        # TODO NOW OR IN FUTURE: handle list[str], align with Action. Maybe allow more deeply nested things too.
        # TODO NOW: should it handle dictionary ids too? Currently this needs overriding _get_outputs. Pattern matching
        # probably not needed for outputs and only for built-in inputs. Even if add more functionality here in future
        # we shoulod still at least the support same as Action.output so it's easy for someone to move from a function
        # action to a class one. In future we'd even like to just allow specifying the component id without the property.

        # Maybe there will be some special built-in behaviour here e.g. to generate outputs automatically from
        # certain reserved arguments like self.targets. Would need to make sure it's not breaking if someone already
        # uses that variable name though.
        pass

    @property
    def _parameters(self) -> set[str]:
        # Note order of parameters doesn't matter since we always handle things with keyword arguments.
        return set(inspect.signature(self.function).parameters)

    @property
    def _runtime_args(self) -> dict[str, IdProperty]:
        # Since function is not a CapturedCallable, input arguments have not yet been bound. They correspond to the
        # model fields that are present in the function signature. This is just the user-specified runtime arguments, as
        # static arguments are not in the function signature (they're in self) and built in runtime arguments are not
        # model fields. These will be of the form {"argument_name": "dropdown.value"}.
        return {arg_name: getattr(self, arg_name) for arg_name in self.model_fields if arg_name in self._parameters}

    @property
    def _action_name(self):
        return self.__class__.__name__
