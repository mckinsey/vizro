"""Global progress indicator component."""

from __future__ import annotations
from dash import html
from vizro.models import VizroBaseModel


class ProgressIndicator(VizroBaseModel):
    """Global progress indicator that shows when actions are running."""

    def build(self) -> html.Span:
        """Build the progress indicator HTML component."""
        return html.Span(
            className="material-symbols-outlined progress_indicator",
            children="forward_media",
        )
