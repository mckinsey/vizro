from typing import Any, Literal

from pydantic import Field

from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models._models_utils import _log_call
from vizro.models.types import ModelID


class collapse_expand_containers(_AbstractAction):
    """Exports visible data of target charts/components.

    Args:
        collapse (list[ModelID]): List of collapsible container ids to collapse.
        expand (list[ModelID]): List of collapsible container ids to expand.
    """
    type: Literal["collapse_expand_containers"] = "collapse_expand_containers"
    collapse: list[ModelID] = Field(default=[], description="List of collapsible container ids to collapse.")
    expand: list[ModelID] = Field(default=[], description="List of collapsible container ids to expand.")
    #  toggle would need multiple state as input. Maybe possible in future but not now. Add new ticket for this
    # toggle: list[str]

    @_log_call
    def pre_build(self):
        from vizro.models import Container

        if not self.collapse and not self.expand:
            raise ValueError("At least one of 'collapse' or 'expand' lists must be defined.")

        user_container_ids = self.collapse + self.expand

        collapsible_container_ids = [
            model.id
            for model in model_manager._get_models(Container, root_model=model_manager._get_model_page(self))
            if model.collapsed is not None
        ]

        invalid_targets = [
            container_id for container_id in user_container_ids if container_id not in collapsible_container_ids
        ]

        if invalid_targets:
            raise ValueError(f"Invalid component IDs found: {invalid_targets}")

        if set(self.collapse) & set(self.expand):
            raise ValueError("Collapse and expand lists cannot contain the same elements!")

    def function(self) -> dict[ModelID, Any]:
        """Collapsed or expand containers on page."""
        return dict.fromkeys(self.collapse, True) | dict.fromkeys(self.expand, False)

    @property
    def outputs(self):  # type: ignore[override]
        return {container_id: f"{container_id}_collapse.is_open" for container_id in self.collapse + self.expand}
