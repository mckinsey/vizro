from typing import Any, Literal

from pydantic import Field, model_validator

from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models._models_utils import _log_call
from vizro.models.types import ModelID


class collapse_expand_containers(_AbstractAction):
    """Exports visible data of target charts/components.

    Args:
        collapse (list[ModelID]): List of collapsible container ids to collapse. Defaults to `[]`.
        expand (list[ModelID]): List of collapsible container ids to expand. Defaults to `[]`.
    """

    type: Literal["collapse_expand_containers"] = "collapse_expand_containers"
    collapse: list[ModelID] = Field(default=[], description="List of collapsible container ids to collapse.")
    expand: list[ModelID] = Field(default=[], description="List of collapsible container ids to expand.")
    #  toggle would need multiple state as input. Maybe possible in future but not now. Add new ticket for this
    # toggle: list[ModelID]

    @model_validator(mode="after")
    def validate_collapse_or_expand_present(self):
        if not self.collapse and not self.expand:
            raise ValueError("Please provide either the `collapse` or `expand` argument.")
        return self

    @model_validator(mode="after")
    def validate_collapse_and_expand_overlap(self):
        if set(self.collapse) & set(self.expand):
            raise ValueError("Collapse and expand lists cannot contain the same elements!")
        return self

    @_log_call
    def pre_build(self):
        from vizro.models import Container

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

    def function(self) -> dict[ModelID, Any]:
        """Collapse or expand containers on page."""
        return dict.fromkeys(self.collapse, True) | dict.fromkeys(self.expand, False)

    @property
    def outputs(self):  # type: ignore[override]
        return {container_id: f"{container_id}_collapse.is_open" for container_id in self.collapse + self.expand}
