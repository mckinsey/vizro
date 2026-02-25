"""Dev app to try things out."""

from typing import Literal

import dash_mantine_components as dmc
import vizro.models as vm
from vizro import Vizro
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call


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
