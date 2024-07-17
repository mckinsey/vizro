"""Page plan model."""

import logging
from typing import List

try:
    from pydantic.v1 import BaseModel, Field, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, validator
from vizro_ai.dashboard.plan.components import ComponentPlan
from vizro_ai.dashboard.plan.controls import ControlPlan
from vizro_ai.dashboard.plan.layout import LayoutPlan

logger = logging.getLogger(__name__)


class PagePlanner(BaseModel):
    """Page plan model."""

    title: str = Field(
        ...,
        description="Title of the page. If no description is provided, "
        "make a short and concise title from the components.",
    )
    components_plan: List[ComponentPlan] = Field(
        ..., description="List of components. Must contain at least one component."
    )
    controls_plan: List[ControlPlan] = Field([], description="Controls of the page.")
    layout_plan: LayoutPlan = Field(None, description="Layout of the page.")

    @validator("components_plan")
    def _check_components_plan(cls, v):
        if len(v) == 0:
            raise ValueError("A page must contain at least one component.")
        return v

    # def create():
    #     pass
