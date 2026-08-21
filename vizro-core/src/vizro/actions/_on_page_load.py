from functools import cached_property
from typing import Literal

from vizro.actions._update_targets import update_targets
from vizro.managers import model_manager
from vizro.models.types import _normalize_action_notifications


class _on_page_load(update_targets):
    """Refreshes the page's figures when the page is opened (or reloaded).

    Identical to [`update_targets`][vizro.actions.update_targets] except that it also writes a page-loaded header to
    the DevTools action log. It is the default action attached to a `Page` and is not intended to be used directly.
    """

    type: Literal["_on_page_load"] = "_on_page_load"  # type: ignore[assignment]

    @cached_property
    def notifications(self):  # type: ignore[override]
        # `_on_page_load` is a private action that fires on every page open/reload/control-reset. A success toast
        # there would be noise, and an error toast would hide the stack trace that developers rely on in the Dash
        # debug panel. So it opts out of notifications entirely (error=None), unlike its public `update_targets` base.
        return _normalize_action_notifications({"error": None})

    @property
    def _log_header(self) -> str:
        # Prepended to this action's DevTools log entry so a page (re)load stands out above the action line. Note this
        # also fires on refresh and after a control reset, since both re-run the on-page-load action - hence "loaded"
        # rather than "opened".
        page = model_manager._get_model_page(self)
        return f'\n=== Page "{page.title}" loaded ===\n'
