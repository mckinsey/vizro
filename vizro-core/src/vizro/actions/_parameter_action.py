from typing import Any, Literal

from dash import ctx
from pydantic import Field

import vizro.models as vm
from vizro.actions._abstract_action import _AbstractAction
from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers import model_manager
from vizro.models.types import ActionNotificationType, ModelID, _Controls


class _parameter(_AbstractAction):
    type: Literal["_parameter"] = "_parameter"

    targets: list[str] = Field(description="Targets in the form `<target_component>.<target_argument>`.")

    notifications: ActionNotificationType  # type: ignore[misc]

    @property
    def _target_ids(self) -> list[ModelID]:
        # This cannot be implemented as PrivateAttr(default_factory=lambda data: ...) because, unlike Field,
        # PrivateAttr does not yet support an argument to the default_factory function. See:
        # https://github.com/pydantic/pydantic/issues/10992
        # Targets without "." are implicitly added by the `Parameter._set_actions` method
        # to handle cases where a dynamic data parameter affects a filter or its targets.
        return [target.partition(".")[0] if "." in target else target for target in self.targets]

    def function(self, _controls: _Controls) -> dict[ModelID, Any]:
        """Applies _controls to charts on page once the page is opened (or refreshed).

        Returns:
            Dict mapping target chart ids to modified figures e.g. {"my_scatter": Figure(...)}.

        """
        # TODO PP IMPORTANT: REMOVE SLEEP AND EXCEPTION AFTER TESTING
        import random
        from time import sleep

        sleep(2)

        if random.random() > 0.5:
            raise Exception("Random error occurred during data export!")

        # This is identical to _on_page_load but with self._target_ids rather than self.targets.
        # TODO-AV2 A 1: _controls is not currently used but instead taken out of the Dash context. This
        # will change in future once the structure of _controls has been worked out and we know how to pass ids through.
        # See https://github.com/mckinsey/vizro/pull/880
        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["_controls"]["filters"],
            ctds_parameter=ctx.args_grouping["external"]["_controls"]["parameters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["_controls"]["filter_interaction"],
            targets=self._target_ids,
        )

    @property
    def outputs(self):  # type: ignore[override]
        # Special handling for vm.Filter as otherwise the filter's default action output would alter the selector value.
        return {
            target: f"{target}.selector" if isinstance(model_manager[target], vm.Filter) else target
            for target in self._target_ids
        }


# TODO PP NOW: Fix this
def rebuild_models():
    # local import inside the function avoids import-time circularity
    from vizro.actions._notifications import show_notification, update_notification

    _parameter.model_rebuild(
        _types_namespace={
            "show_notification": show_notification,
            "update_notification": update_notification,
        }
    )


rebuild_models()
