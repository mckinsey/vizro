from typing import Literal

from vizro.actions._update_targets import update_targets
from vizro.managers import model_manager


class _on_page_load(update_targets):
    """Refreshes the page's figures when the page is opened (or reloaded).

    Identical to [`update_targets`][vizro.actions.update_targets] except that it also writes a page-loaded header to
    the DevTools action log. It is the default action attached to a `Page` and is not intended to be used directly.
    """

    type: Literal["_on_page_load"] = "_on_page_load"  # type: ignore[assignment]

    @property
    def _log_header(self) -> str:
        # Prepended to this action's DevTools log entry so a page (re)load stands out above the action line. Note this
        # also fires on refresh and after a control reset, since both re-run the on-page-load action - hence "loaded"
        # rather than "opened".
        page = model_manager._get_model_page(self)
        return f'\n=== Page "{page.title}" loaded ===\n'
