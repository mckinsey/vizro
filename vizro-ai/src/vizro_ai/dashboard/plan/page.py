"""Page plan model."""

import logging
from typing import List

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field
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
    components_plan: List[ComponentPlan]
    controls_plan: List[ControlPlan] = Field([], description="Controls of the page.")
    layout_plan: LayoutPlan = Field(None, description="Layout of the page.")
