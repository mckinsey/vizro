"""Helper Functions For Vizro AI dashboard."""

from dataclasses import dataclass
from typing import Any

import tqdm.std
import vizro.models as vm


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
