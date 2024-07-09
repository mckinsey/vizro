"""Helper Functions For Vizro AI dashboard."""

from dataclasses import dataclass

import vizro.models as vm


@dataclass
class DashboardOutputs:
    """Dataclass containing all possible `VizroAI.dashboard()` output."""

    code: str
    dashboard: vm.Dashboard

def _execute_step(pbar, description, value):
    pbar.set_description_str(description)
    pbar.update(1)
    pbar.refresh()
    return value
