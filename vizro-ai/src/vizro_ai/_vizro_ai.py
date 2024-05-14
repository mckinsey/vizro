import logging
from typing import Any, Dict, Optional, Union

import pandas as pd
import plotly.graph_objects as go
from langchain_openai import ChatOpenAI

from vizro_ai.chains._llm_models import _get_llm_model
from vizro_ai.components import GetCodeExplanation, GetDebugger
from vizro_ai.task_pipeline._pipeline_manager import PipelineManager
from vizro_ai.utils.helper import (
    DebugFailure,
    _debug_helper,
    _exec_code_and_retrieve_fig,
    _exec_fig_code_display_markdown,
    _is_jupyter,
)

logger = logging.getLogger(__name__)


class VizroAI:
    """Vizro-AI main class."""

    pipeline_manager: PipelineManager = PipelineManager()
    _return_all_text: bool = False

    def __init__(self, model: Optional[Union[ChatOpenAI, str]] = None):
        """Initialization of VizroAI.

        Args:
            model: model instance or model name.

        """
        self.model = _get_llm_model(model=model)
        self.components_instances = {}

        # TODO add pending URL link to docs
        logger.info(
            f"You have selected {self.model.model_name},"
            f"Engaging with LLMs (Large Language Models) carries certain risks. "
            f"Users are advised to become familiar with these risks to make informed decisions, "
            f"and visit this page for detailed information: "
            "https://vizro-ai.readthedocs.io/en/latest/pages/explanation/disclaimer/"
        )
        self._set_task_pipeline_llm()

    def _set_task_pipeline_llm(self) -> None:
        self.pipeline_manager.llm = self.model

    # TODO delete after adding debug in pipeline
    def _lazy_get_component(self, component_class: Any) -> Any:  # TODO configure component_class type
        """Lazy initialization of components."""
        if component_class not in self.components_instances:
            self.components_instances[component_class] = component_class(llm=self.model)
        return self.components_instances[component_class]

    def _run_plot_tasks(
        self, df: pd.DataFrame, user_input: str, max_debug_retry: int = 3, explain: bool = False
    ) -> Dict[str, Any]:
        """Task execution."""
        chart_type_pipeline = self.pipeline_manager.chart_type_pipeline
        chart_types = chart_type_pipeline.run(initial_args={"chain_input": user_input, "df": df})

        # TODO update to loop through charts for multiple charts creation
        plot_pipeline = self.pipeline_manager.plot_pipeline
        custom_chart_code = plot_pipeline.run(
            initial_args={"chain_input": user_input, "df": df, "chart_types": chart_types}
        )

        # TODO add debug in pipeline after getting _debug_helper logic in component
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

    def plot(
        self, df: pd.DataFrame, user_input: str, explain: bool = False, max_debug_retry: int = 3
    ) -> Union[go.Figure, Dict[str, Any]]:
        """Plot visuals using vizro via english descriptions, english to chart translation.

        Args:
            df: The dataframe to be analyzed.
            user_input: User questions or descriptions of the desired visual.
            explain: Flag to include explanation in response.
            max_debug_retry: Maximum number of retries to debug errors. Defaults to `3`.

        Returns:
            Plotly Figure object or a dictionary containing data

        """
        output_dict = self._run_plot_tasks(df, user_input, explain=explain, max_debug_retry=max_debug_retry)
        code_string = output_dict.get("code_string")
        business_insights = output_dict.get("business_insights")
        code_explanation = output_dict.get("code_explanation")

        if code_string.startswith("Failed to debug code"):
            raise DebugFailure(
                "Chart creation failed. Retry debugging has reached maximum limit. Try to rephrase the prompt, "
                "or try to select a different model. Fallout response is provided: \n\n" + code_string
            )

        # TODO Tentative for integration test
        if self._return_all_text:
            return output_dict
        if not explain:
            return _exec_code_and_retrieve_fig(code=code_string, local_args={"df": df}, is_notebook_env=_is_jupyter())
        if explain:
            return _exec_fig_code_display_markdown(
                df=df, code_snippet=code_string, biz_insights=business_insights, code_explain=code_explanation
            )
