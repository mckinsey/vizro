"""Dashboard plan model."""

import logging
from typing import List

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field
from vizro_ai.dashboard.response_models.page import PagePlanner

logger = logging.getLogger(__name__)


class DashboardPlanner(BaseModel):
    """Dashboard plan model."""

    title: str = Field(
        ...,
        description="Title of the dashboard. If no description is provided,"
        " make a short and concise title from the content of the pages.",
    )
    pages: List[PagePlanner]
