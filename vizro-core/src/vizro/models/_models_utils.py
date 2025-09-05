import logging
import warnings
from functools import wraps

from dash import html
from pydantic import ValidationInfo

from vizro.managers import model_manager
from vizro.models.types import CapturedCallable, _SupportsCapturedCallable

logger = logging.getLogger(__name__)


def _log_call(method):
    @wraps(method)
    def _wrapper(self, *args, **kwargs):
        # We need to run method before logging so that @_log_call works for __init__.
        return_value = method(self, *args, **kwargs)
        logger.debug("Running %s.%s for model with id %s", self.__class__.__name__, method.__name__, self.id)
        return return_value

    return _wrapper


# Validators for reuse
def check_captured_callable_model(value):
    if isinstance(value, CapturedCallable):
        captured_callable = value
    elif isinstance(value, _SupportsCapturedCallable):
        captured_callable = value._captured_callable
    else:
        return value

    raise ValueError(
        f"A callable of mode `{captured_callable._mode}` has been provided. Please wrap it inside "
        f"`{captured_callable._model_example}`."
    )


REPLACEMENT_STRINGS = {
    # "substring to match a larger general module string": "string to replace with"
    # dot required so that in the case where no replacement is used, we do not
    # have a preceding dot (see __repr_clean__ in types.py)
    "plotly.express": "px.",
    "vizro.tables": "vt.",
    "vizro.figures": "vf.",
    "vizro.actions": "va.",
    "vizro.charts": "vc.",
}


def _build_inner_layout(layout, components):
    """Builds inner layout and adds components to grid or flex. Used inside `Page`, `Container` and `Form`."""
    from vizro.models import Grid

    components_container = layout.build()
    if isinstance(layout, Grid):
        for idx, component in enumerate(components):
            components_container[f"{layout.id}_{idx}"].children = component.build()
    else:
        components_container.children = [html.Div(component.build(), className="flex-item") for component in components]

    return components_container


def validate_icon(icon) -> str:
    return icon.strip().lower().replace(" ", "_")


def warn_description_without_title(description, info: ValidationInfo):
    title = info.data.get("title")

    if description and not title:
        warnings.warn(
            """
            The `description` field is set, but `title` is missing or empty.
            The tooltip will not appear unless a `title` is provided.
            """,
            UserWarning,
        )
    return description


def make_actions_chain(self):
    """Creates actions chain from a list of actions.

    Ideally this would have been implemented as an AfterValidator for the actions field, but we need access to
    action_triggers property, which needs the parent model instance. Hence, it must be done as a model validator.

    This runs after model_post_init so that self._inner_component_id will have already been set correctly in
    Table and AgGrid. Even though it's a model validator it is also run on assignment e.g. selector.actions = ...
    """
    from vizro.actions import export_data, filter_interaction
    from vizro.actions._on_page_load import _on_page_load

    converted_actions = []

    # Convert any built in actions written in the legacy style vm.Action(function=filter_interaction(...)) or
    # vm.Action(function=export_data(...)) to the new style filter_interaction(...) or export_data(...).
    # We need to delete the old action models from the model manager so they don't get built. After that,
    # built in actions are always handled in the new way.
    for action in self.actions:
        if isinstance(action.function, (export_data, filter_interaction)):
            del model_manager[action.id]
            converted_actions.append(action.function)
        else:
            converted_actions.append(action)

    model_action_trigger = self._action_triggers["__default__"]
    for i, action in enumerate(converted_actions):
        # First action in the chain uses the model's specified trigger.
        # All subsequent actions in the chain are triggered by the previous action's completion.
        # In the future, we would allow multiple keys in the _action_triggers dictionary, and then we'd need to look up
        # the relevant entry here. For now there's just __default__ so we always use that.
        action._trigger = model_action_trigger if i == 0 else f"{converted_actions[i - 1].id}_finished.data"

        # Every action has to know about the model action trigger to properly set the action's builtin arg "_trigger".
        action._first_in_chain_trigger = model_action_trigger

        # The actions chain guard should be called only for on page load.
        action._prevent_initial_call_of_guard = not isinstance(action, _on_page_load)

        # Temporary hack to help with lookups in filter_interaction. Should not be required in future with reworking of
        # model manager and removal of filter_interaction.
        action._parent_model = self.id

    # We should do self.actions = converted_actions but this leads to a recursion error. The below is a workaround
    # until the pydantic bug is fixed. See https://github.com/pydantic/pydantic/issues/6597.
    self.__dict__["actions"] = converted_actions
    return self
