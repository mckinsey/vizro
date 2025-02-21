"""Dashboard plan model."""

import logging

from pydantic import BaseModel, Field

from vizro_ai.dashboard._response_models.page import PagePlan

logger = logging.getLogger(__name__)


class DashboardPlan(BaseModel):
    """Dashboard plan model."""

    title: str = Field(
        description="""
        Title of the dashboard. If no description is provided,
        make a short and concise title from the content of the pages.
        """,
    )
    pages: list[PagePlan]
