import logging
import warnings
from functools import wraps

from dash import html
from dash.development.base_component import Component
from pydantic import ValidationInfo

from vizro.models.types import CapturedCallable, _SupportsCapturedCallable

logger = logging.getLogger(__name__)


def _all_hidden(components: Component | list[Component]):
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
    """Builds an inner layout and adds components to a grid or flex. Used inside `Page`, `Container` and `Form`."""
    from vizro.models import Grid

    components_container = layout.build()
    if isinstance(layout, Grid):
        for idx, component in enumerate(components):
            components_container[f"{layout.id}_{idx}"].children = component.build()
    else:
        components_container.children = [html.Div(component.build(), className="flex-item") for component in components]

    return components_container


def validate_icon(icon: str) -> str:
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
    """Creates an actions chain from a list of actions.

    Ideally this would have been implemented as an AfterValidator for the actions field, but we need access to
    action_triggers property, which needs the parent model instance. Hence, it must be done as a model validator.

    This runs after model_post_init so that self._inner_component_id will have already been set correctly in
    Table. Even though it's a model validator it is also run on assignment e.g. selector.actions = ...
    """
    model_action_trigger = self._action_triggers["__default__"]

    # Models whose chain fires on page load (i.e. Page) run their first action on the initial page render. For every
    # other model (Button, controls, ...) the chain only runs in response to a genuine user interaction. This used to be
    # keyed off `isinstance(action, _on_page_load)`, but now that users can supply their own `Page.actions` the "run on
    # load" behavior belongs to the triggering model, not to a specific action type.
    fires_on_load = getattr(self, "_actions_chain_fires_on_load", False)

    for i, action in enumerate(self.actions):
        # First action in the chain uses the model's specified trigger.
        # All subsequent actions in the chain are triggered by the previous action's completion.
        # In the future, we would permit multiple keys in the _action_triggers dictionary, and then we'd need to look up
        # the relevant entry here. For now there's just __default__ so we always use that.
        action._trigger = model_action_trigger if i == 0 else f"{self.actions[i - 1].id}_finished.data"

        # Every action has to know about the model action trigger to properly set the action's builtin arg "_trigger".
        action._first_in_chain_trigger = model_action_trigger

        # The guard prevents the initial call for every action except the first one in a chain that fires on page load,
        # which must run when the page layout is first rendered. Subsequent actions in any chain are triggered by the
        # previous action finishing rather than the initial render, so their guard always prevents the initial call.
        action._prevent_initial_call_of_guard = not (i == 0 and fires_on_load)

        # Temporary workaround for lookups in set_controls. This should become unnecessary once the model manager
        # supports `parent_model` access for all Vizro models.
        action._parent_model = self

    return self
