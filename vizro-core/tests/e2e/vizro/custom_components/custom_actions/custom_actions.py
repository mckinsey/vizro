import time
from typing import Optional

from vizro.models.types import capture


@capture("action")
def scatter_click_data_custom_action(click_data: Optional[dict] = None):
    """Custom action."""
    if click_data:
        time.sleep(2)  # sleep needed here for easy testing of progress indicator for running actions
        return f'Scatter chart clicked data:\n### Species: "{click_data["points"][0]["customdata"][0]}"'
    return "### No data clicked."
