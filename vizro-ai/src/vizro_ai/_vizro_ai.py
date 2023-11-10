import logging
import traceback
from typing import Any, Callable, Dict, Optional, Union

import pandas as pd

from vizro_ai.chains import ModelConstructor
from vizro_ai.chains._llm_models import LLM_MODELS
from vizro_ai.components import (
    GetChartSelection,
    GetCodeExplanation,
    GetCustomChart,
    GetDataFrameCraft,
    GetDebugger,
    GetVisualCode,
)
from vizro_ai.utils import _safeguard_check

logger = logging.getLogger(__name__)


class DebugFailure(Exception):
    pass


class VizroAI:
    """Vizro-AI main class."""

    model_constructor: ModelConstructor = ModelConstructor()
    _return_all_text: bool = False

    def __init__(self, model_name: str = "gpt-3.5-turbo-0613", temperature: int = 0):
        """Initialization of VizroAI.

        Args:
            model_name: Model name in string format.
            temperature: Temperature parameter for LLM.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.components_instances = {}
        self._llm_to_use = None
        # TODO add pending URL link to docs
        logger.info(
            f"You have selected {self.model_name},"
            f"Engaging with LLMs (Large Language Models) carries certain risks. "
            f"Users are advised to become familiar with these risks to make informed decisions, "
            f"and visit this page for detailed information: "
            "https://vizro-ai.readthedocs.io/en/latest/pages/explanation/disclaimer/"
        )

    @property
    def llm_to_use(self) -> LLM_MODELS:
        _llm_to_use = self.model_constructor.get_llm_model(self.model_name, self.temperature)
        return _llm_to_use

    def _lazy_get_component(self, component_class: Any) -> Any:  # TODO configure component_class type
        """Lazy initialization of components."""
        if component_class not in self.components_instances:
            self.components_instances[component_class] = component_class(llm=self.llm_to_use)
        return self.components_instances[component_class]

    def _run_plot_tasks(
        self, df: pd.DataFrame, user_input: str, max_debug_retry: int = 3, explain: bool = False
    ) -> Dict[str, Any]:
        """Task execution."""
        target_chart = self._lazy_get_component(GetChartSelection).run(df=df, chain_input=user_input)
        df_code = self._lazy_get_component(GetDataFrameCraft).run(df=df, chain_input=user_input)
        visual_code = self._lazy_get_component(GetVisualCode).run(
            chain_input=user_input, chart_types=target_chart, df_code=df_code
        )
        custom_chart_code = self._lazy_get_component(GetCustomChart).run(chain_input=visual_code)

        fix_func = self._lazy_get_component(GetDebugger).run
        validated_code_dict = _debug_helper(
            code_string=custom_chart_code, max_debug_retry=max_debug_retry, fix_chain=fix_func, df=df
        )

        pass_validation = validated_code_dict.get("debug_status")
        code_string = validated_code_dict.get("code_string")
        business_insights, code_explanation = None, None

        if explain and pass_validation:
            business_insights, code_explanation = self._lazy_get_component(GetCodeExplanation).run(
                chain_input=user_input, code_snippet=code_string
            )

        return {
            "business_insights": business_insights,
            "code_explanation": code_explanation,
            "code_string": code_string,
        }

    def _get_chart_code(self, df: pd.DataFrame, user_input: str) -> str:
        """Get Chart code of vizro via english descriptions, English to chart translation.

        Can be used in integration with other application if only code snippet return is required.

        Args:
            df: The dataframe to be analyzed
            user_input: User questions or descriptions of the desired visual
        """
        # TODO refine and update error handling
        return self._run_plot_tasks(df, user_input, explain=False).get("code_string")

    def plot(self, df: pd.DataFrame, user_input: str, explain: bool = False) -> Union[None, Dict[str, Any]]:
        """Plot visuals using vizro via english descriptions, english to chart translation.

        Args:
            df: The dataframe to be analyzed
            user_input: User questions or descriptions of the desired visual
            explain: Flag to include explanation in response
        """
        output_dict = self._run_plot_tasks(df, user_input, explain=explain)
        code_string = output_dict.get("code_string")
        business_insights = output_dict.get("business_insights")
        code_explanation = output_dict.get("code_explanation")

        if code_string.startswith("Failed to debug code"):
            raise DebugFailure(
                "Chart creation failed. Retry debugging has reached maximum limit. Try to rephrase the prompt, "
                "or try to select a different model. Fallout response is provided: \n\n" + code_string
            )
        if not explain:
            _exec_code(code=code_string, local_args={"df": df}, show_fig=True, is_notebook_env=_is_jupyter())
        if explain:
            _display_markdown_and_chart(
                df=df, code_snippet=code_string, biz_insights=business_insights, code_explain=code_explanation
            )
        # TODO Tentative for integration test
        if self._return_all_text:
            return output_dict


def _debug_helper(
    code_string: str, max_debug_retry: int, fix_chain: Callable, df: pd.DataFrame = None
) -> Dict[bool, str]:
    """Debugging helper."""
    # TODO plug logic back into component
    retry_success = False
    last_exception = None
    for attempt in range(max_debug_retry):
        try:
            _exec_code(code=code_string, local_args={"df": df}, is_notebook_env=_is_jupyter())
            retry_success = True
            break
        except Exception as e:
            error_info = f"{traceback.format_exc()}"
            code_string = fix_chain(chain_input=error_info, code_snippet=code_string)
            last_exception = e

    code_string = code_string if retry_success else f"Failed to debug code {code_string}, error: {last_exception}"

    return {"debug_status": retry_success, "code_string": code_string}


def _exec_code(
    code: str, local_args: Optional[Dict] = None, show_fig: bool = False, is_notebook_env: bool = True
) -> None:
    """Execute code in notebook with correct namespace."""
    from IPython import get_ipython

    if show_fig and "\nfig.show()" not in code:
        code += "\nfig.show()"
    elif not show_fig:
        code = code.replace("fig.show()", "")
    namespace = get_ipython().user_ns if is_notebook_env else globals()
    if local_args:
        namespace.update(local_args)
    _safeguard_check(code)

    exec(code, namespace)  # nosec


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


def _display_markdown_and_chart(df: pd.DataFrame, code_snippet: str, biz_insights: str, code_explain: str) -> None:
    # TODO change default test str to other
    """Display chart and Markdown format description in jupyter."""
    try:
        # pylint: disable=import-outside-toplevel
        from IPython.display import Markdown, display
    except Exception as exc:
        raise ImportError("Please install IPython before proceeding in jupyter environment.") from exc
    # TODO clean up the formatting markdown code
    markdown_code = f"```\n{code_snippet}\n```"
    output_text = f"<h4>Insights:</h4>\n\n{biz_insights}\n<br><br><h4>Code:</h4>\n\n{code_explain}\n{markdown_code}"
    display(Markdown(output_text))
    _exec_code(code_snippet, local_args={"df": df}, show_fig=True, is_notebook_env=_is_jupyter())
