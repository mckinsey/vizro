from typing import Any, Literal

from pydantic import Field, model_validator

from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models._models_utils import _log_call
from vizro.models.types import ModelID


class collapse_expand_containers(_AbstractAction):
    """Collapses and/or expands selected collapsible containers.

    Args:
        collapse (list[ModelID]): List of collapsible container ids to collapse. Defaults to `[]`.
        expand (list[ModelID]): List of collapsible container ids to expand. Defaults to `[]`.
    """

    type: Literal["collapse_expand_containers"] = "collapse_expand_containers"
    collapse: list[ModelID] = Field(default=[], description="List of collapsible container ids to collapse.")
    expand: list[ModelID] = Field(default=[], description="List of collapsible container ids to expand.")
    # TODO-AV2 D 5: toggle would need multiple state as input. Make that built-in actions can deal with arbitrary
    #  number of inputs.
    # toggle: list[ModelID]

    @model_validator(mode="after")
    def validate_collapse_and_expand(self):
        if not self.collapse and not self.expand:
            raise ValueError("Either the `collapse` or `expand` list must contain at least a single element.")
        if overlap := set(self.collapse) & set(self.expand):
            raise ValueError(f"`collapse` and `expand` cannot both contain the same IDs {overlap}.")
        return self

    @_log_call
    def pre_build(self):
        from vizro.models import Container

        page_collapsible_container_ids = {
            model.id
            for model in model_manager._get_models(Container, root_model=model_manager._get_model_page(self))
            if model.collapsed is not None
        }

        invalid_ids = (set(self.collapse) | set(self.expand)) - page_collapsible_container_ids

        if invalid_ids:
            raise ValueError(
                f"Invalid component IDs found: {invalid_ids}."
                " Action's collapse and expand IDs must be collapsible containers on the same page as the action."
            )

    def function(self) -> dict[ModelID, Any]:
        """Collapse or expand containers on page."""
        return dict.fromkeys(self.collapse, True) | dict.fromkeys(self.expand, False)

    @property
    def outputs(self):  # type: ignore[override]
        return {container_id: f"{container_id}_collapse.is_open" for container_id in self.collapse + self.expand}
