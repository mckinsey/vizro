import logging
from functools import wraps
from typing import Optional, Union

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage

from vizro_ai._llm_models import _get_llm_model, _get_model_name
from vizro_ai.dashboard._graph.dashboard_creation import _create_and_compile_graph
from vizro_ai.dashboard._pydantic_output import _get_pydantic_model  # TODO: make general, ie remove from dashboard
from vizro_ai.dashboard.utils import DashboardOutputs, _extract_overall_imports_and_code, _register_data
from vizro_ai.plot._response_models import ChartPlan, ChartPlanFactory
from vizro_ai.utils.helper import _get_df_info

logger = logging.getLogger(__name__)


def deprecate_explain(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "explain" in kwargs:
            raise TypeError(
                """VizroAI.plot() no longer supports the 'explain' parameter.
This parameter has been removed with the release of `0.3.0`. If you need explanations, use
`return_elements=True` and the attributes `chart_insights` and `code_explanation`:

res = vizro_ai.plot(df, user_input, return_elements=True)
print(res.chart_insights)
print(res.code_explanation)"""
            )
        return func(*args, **kwargs)

    return wrapper


class VizroAI:
    """Vizro-AI main class."""

    def __init__(self, model: Optional[Union[BaseChatModel, str]] = None):
        """Initialization of VizroAI.

        Args:
            model: model instance or model name.

        """
        self.model = _get_llm_model(model=model)
        self.components_instances = {}

        # TODO add pending URL link to docs
        model_name = _get_model_name(self.model)
        logger.info(
            f"You have selected {model_name},"
            f"Engaging with LLMs (Large Language Models) carries certain risks. "
            f"Users are advised to become familiar with these risks to make informed decisions, "
            f"and visit this page for detailed information: "
            "https://vizro-ai.readthedocs.io/en/latest/pages/explanation/disclaimer/"
        )

    @deprecate_explain
    def plot(
        self,
        df: pd.DataFrame,
        user_input: str,
        max_debug_retry: int = 1,
        return_elements: bool = False,
        validate_code: bool = True,
    ) -> Union[go.Figure, ChartPlan]:
        """Plot visuals using vizro via english descriptions, english to chart translation.

        Args:
            df: The dataframe to be analyzed.
            user_input: User questions or descriptions of the desired visual.
            max_debug_retry: Maximum number of retries to debug errors. Defaults to `1`.
            return_elements: Flag to return ChartPlan pydantic model that includes all
                possible elements generated. Defaults to `False`.
            validate_code: Flag if produced code should be executed to validate it. Defaults to `True`.

        Returns:
            go.Figure or ChartPlan pydantic model

        """
        response_model = ChartPlanFactory(data_frame=df) if validate_code else ChartPlan
        _, df_sample = _get_df_info(df, n_sample=10)
        response = _get_pydantic_model(
            query=user_input,
            llm_model=self.model,
            response_model=response_model,
            df_info=df_sample,
            max_retry=max_debug_retry,
        )
        if return_elements:
            return response
        else:
            return response.get_fig_object(data_frame=df)

    def dashboard(
        self,
        dfs: list[pd.DataFrame],
        user_input: str,
        return_elements: bool = False,
    ) -> Union[DashboardOutputs, vm.Dashboard]:
        """Creates a Vizro dashboard using english descriptions.

        Args:
            dfs: The dataframes to be analyzed.
            user_input: User questions or descriptions of the desired visual.
            return_elements: Flag to return DashboardOutputs dataclass that includes all possible elements generated.

        Returns:
            vm.Dashboard or DashboardOutputs dataclass.

        """
        runnable = _create_and_compile_graph()

        config = {"configurable": {"model": self.model}}
        message_res = runnable.invoke(
            {
                "dfs": dfs,
                "all_df_metadata": {},
                "dashboard_plan": None,
                "pages": [],
                "dashboard": None,
                "messages": [HumanMessage(content=user_input)],
                "custom_charts_code": [],
                "custom_charts_imports": [],
            },
            config=config,
        )
        dashboard = message_res["dashboard"]
        _register_data(all_df_metadata=message_res["all_df_metadata"])

        if return_elements:
            chart_code, imports = _extract_overall_imports_and_code(
                message_res["custom_charts_code"], message_res["custom_charts_imports"]
            )
            code = dashboard._to_python(extra_callable_defs=chart_code, extra_imports=imports)
            dashboard_output = DashboardOutputs(dashboard=dashboard, code=code)
            return dashboard_output
        else:
            return dashboard
