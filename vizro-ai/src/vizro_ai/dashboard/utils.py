"""Helper Functions For Vizro AI dashboard."""

from dataclasses import dataclass

# import black
from typing import Any

import tqdm.std
import vizro.models as vm

IMPORT_STATEMENTS = (
    "import vizro.plotly.express as px\n"
    "from vizro.models.types import capture\n"
    "import plotly.graph_objects as go\n"
    "from vizro.tables import dash_ag_grid\n"
    "import vizro.models as vm\n"
)


@dataclass
class DashboardOutputs:
    """Dataclass containing all possible `VizroAI.dashboard()` output."""

    code: str
    dashboard: vm.Dashboard


def _execute_step(pbar: tqdm.std.tqdm, description: str, value: Any) -> Any:
    pbar.set_description_str(description)
    pbar.update(1)
    pbar.refresh()
    return value


# is duplicated in vizro-ai/src/vizro_ai/utils/helper.py
# to be consolidated in a common file
def _is_jupyter() -> bool:  # pragma: no cover
    """Checks if we're running in a Jupyter notebook."""
    try:
        from IPython import get_ipython
    except NameError:
        return False
    ipython = get_ipython()
    shell = ipython.__class__.__name__
    if "google.colab" in str(ipython.__class__) or shell == "ZMQInteractiveShell":
        return True  # Jupyter notebook or qtconsole
    elif shell == "TerminalInteractiveShell":
        return False  # Terminal running IPython
    else:
        return False  # Other type (?)


def _get_tqdm():
    if _is_jupyter():
        from tqdm.notebook import tqdm, trange
    else:
        from tqdm import tqdm, trange
    return tqdm, trange


def _dashboard_code(dashboard: vm.Dashboard) -> str:
    """Generate dashboard code from dashboard object."""
    dashboard_code_str = IMPORT_STATEMENTS + repr(dashboard)

    # TODO: use black or ruff to format the code
    # formatted_code = black.format_str(dashboard_code_str, mode=black.Mode())
    return dashboard_code_str
