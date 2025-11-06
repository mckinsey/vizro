import logging
import warnings
from functools import wraps
from typing import Any, Union

from dash import html
from dash.development.base_component import Component
from pydantic import ValidationInfo

from vizro.managers import model_manager
from vizro.models.types import CapturedCallable, _SupportsCapturedCallable

logger = logging.getLogger(__name__)


def _all_hidden(components: Union[Component, list[Component]]):
    """Returns True if all `components` are either None and/or have hidden=True and/or className contains `d-none`."""
    if isinstance(components, Component):
        components = [components]
    return all(
        component is None
        or getattr(component, "hidden", False)
        or "d-none" in getattr(component, "className", "d-inline")
        for component in components
    )


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


# We use this as a validator to deprecate a field, instead of setting deprecate=True, which only affects the JSON schema
# and raises unwanted warnings when looking through model attributes. deprecate=True wouldn't be sufficient anyway,
# since:
# - the warning isn't raised on model instantiation, just on field access
# - the warning category can't be changed from the default DeprecationWarning to FutureWarning and so will not be
# visible to most users
# These are known limitations with pydantic's current implementation; see
# https://github.com/pydantic/pydantic/issues/8922 and https://docs.pydantic.dev/latest/concepts/fields/.
# This only runs if the field is explicitly set since validate_default=False by default.
# This does not add anything to the API docs. You must add a note to the field docstring manually.
def make_deprecated_field_warning(message: str, /):
    def deprecate_field(value: Any, info: ValidationInfo):
        warnings.warn(
            f"The `{info.field_name}` argument is deprecated and will not exist in Vizro 0.2.0. {message}.",
            category=FutureWarning,
            stacklevel=3,
        )
        return value

    return deprecate_field


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
            action_name = action.function._action_name
            warnings.warn(
                f"Using the `Action` model for the built-in action `{action_name}` is deprecated and will not be"
                f" possible in Vizro 0.2.0. Call the action directly with `actions=va.{action_name}(...)`. See "
                "https://vizro.readthedocs.io/en/stable/pages/API-reference/deprecations/#action-model-for-built-in"
                "-action.",
                category=FutureWarning,
                stacklevel=4,
            )

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

        # Temporary workaround for lookups in filter_interaction and set_control. This should become unnecessary once
        # the model manager supports `parent_model` access for all Vizro models.
        action._parent_model = self

    # We should do self.actions = converted_actions but this leads to a recursion error. The below is a workaround
    # until the pydantic bug is fixed. See https://github.com/pydantic/pydantic/issues/6597.
    self.__dict__["actions"] = converted_actions
    return self
