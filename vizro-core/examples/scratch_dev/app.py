"""Dev app to try things out."""

from typing import Literal

from dash import html
import dash_mantine_components as dmc
import vizro.models as vm
from vizro import Vizro
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

# Shared layout constants
GAP = "20px"
CARD_TITLE_SIZE = "md"
SECTION_LABEL_SIZE = "sm"


def _section_label(text: str):
    """Section heading inside a card (e.g. 'Anchor', 'Breadcrumbs')."""
    return dmc.Text(text, size=SECTION_LABEL_SIZE, fw=600, c="dimmed", mb="xs")


class Timeline(VizroBaseModel):
    """Based on dmc.Timeline component."""

    type: Literal["timeline"] = "timeline"

    @_log_call
    def build(self):
        """Return dmc.Timeline component."""
        return dmc.Timeline(
            active=1,
            children=[
                dmc.TimelineItem(
                    title="Step one",
                    children=dmc.Text("First event description.", c="dimmed", size="sm"),
                ),
                dmc.TimelineItem(
                    title="Step two",
                    children=dmc.Text("Second event description.", c="dimmed", size="sm"),
                ),
                dmc.TimelineItem(
                    title="Step three",
                    lineVariant="dashed",
                    children=dmc.Text("Third event (dashed line).", c="dimmed", size="sm"),
                ),
            ],
        )


vm.Page.add_type("components", Timeline)

dashboard = vm.Dashboard(
    pages=[vm.Page(title="Embed dmc component", components=[Timeline()])],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
