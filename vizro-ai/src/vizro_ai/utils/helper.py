"""Helper Functions For Vizro AI."""

import traceback
from typing import Callable, Dict, Optional

import pandas as pd
import plotly.graph_objects as go

from .safeguard import _safeguard_check


# Taken from rich.console. See https://github.com/Textualize/rich.
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


def _debug_helper(
    code_string: str, max_debug_retry: int, fix_chain: Callable, df: pd.DataFrame = None
) -> Dict[bool, str]:
    """Debugging helper."""
    retry_success = False
    last_exception = None
    is_jupyter = _is_jupyter()
    for attempt in range(max_debug_retry):
        try:
            _exec_code_and_retrieve_fig(code=code_string, local_args={"df": df}, is_notebook_env=is_jupyter)
            retry_success = True
            break
        except Exception as e:
            error_info = f"{traceback.format_exc()}"
            code_string = fix_chain(chain_input=error_info, code_snippet=code_string)
            last_exception = e

    code_string = code_string if retry_success else f"Failed to debug code {code_string}, error: {last_exception}"

    return {"debug_status": retry_success, "code_string": code_string}


def _exec_code_and_retrieve_fig(
    code: str, local_args: Optional[Dict] = None, is_notebook_env: bool = True
) -> go.Figure:
    """Execute code in notebook with correct namespace and return fig object.

    Args:
        code: code string to be executed
        local_args: additional local arguments
        is_notebook_env: boolean flag indicating if code is run in Jupyter notebook

    Returns:
        go.Figure

    """
    from IPython import get_ipython

    namespace = get_ipython().user_ns if is_notebook_env else globals()
    if local_args:
        namespace.update(local_args)
    _safeguard_check(code)

    exec(code, namespace)  # nosec

    dashboard_ready_fig = namespace["fig"]
    return dashboard_ready_fig


def _exec_fig_code_display_markdown(
    df: pd.DataFrame, code_snippet: str, biz_insights: str, code_explain: str
) -> go.Figure:
    # TODO change default test str to other
    """Display chart and Markdown format description in jupyter and returns fig object.

    Args:
        df: The dataframe to be analyzed.
        code_snippet: code string to be executed
        biz_insights: business insights to be displayed in markdown cell
        code_explain: code explanation to be displayed in markdown cell

    Returns:
        go.Figure

    """
    try:
        # pylint: disable=import-outside-toplevel
        from IPython.display import Markdown, display
    except Exception as exc:
        raise ImportError("Please install IPython before proceeding in jupyter environment.") from exc
    # TODO clean up the formatting markdown code to render in jupyter
    markdown_code = f"```\n{code_snippet}\n```"
    output_text = f"<h4>Insights:</h4>\n\n{biz_insights}\n<br><br><h4>Code:</h4>\n\n{code_explain}\n{markdown_code}"
    display(Markdown(output_text))
    return _exec_code_and_retrieve_fig(code_snippet, local_args={"df": df}, is_notebook_env=_is_jupyter())


class DebugFailure(Exception):
    """Debug Failure."""

    pass
