"""Chart Type Selection Component."""

from typing import Dict, Tuple

import pandas as pd

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field

from vizro_ai.chains._chain_utils import _log_time
from vizro_ai.chains._llm_models import LLM_MODELS
from vizro_ai.components import VizroAiComponentBase
from vizro_ai.schema_manager import SchemaManager

# initialization of schema manager, and register schema needed
# preprocess: llm kwargs for function description schema + partial vars
# post process: clean up the response and gets exact the output of this component

# 1. Define schema
openai_schema_manager = SchemaManager()


@openai_schema_manager.register
class ChartSelection(BaseModel):
    """Choose the chart that best to describes the user request or given data."""

    # TODO enable multiple charts later
    # chart_type: Union[str, List[str]] = Field(
    #     ..., description="chart type, e.g. bar or a list of chart, e.g. [bar, line, pie]"
    # )
    chart_type: str = Field(..., description="chart type, e.g. bar")


# 2. Define prompt
chart_type_prompt = "choose a best chart types for this df info:{df_schema}, {df_head} and user question {input}?"


# 3. Define Component
class GetChartSelection(VizroAiComponentBase):
    """Get Chart Types.

    Attributes
        prompt (str): Prompt chart selection chains.

    """

    prompt: str = chart_type_prompt

    def __init__(self, llm: LLM_MODELS):
        """Initialization of Chart Selection components.

        Args:
            llm: LLM model wrapped with Langchain wrapper

        """
        super().__init__(llm)

    def _pre_process(self, df: pd.DataFrame, *args, **kwargs) -> Tuple[Dict, Dict]:
        """Preprocess for chart selections.

        It should return llm_kwargs and partial_vars_map for
        """
        df_schema, df_head = self._get_df_info(df)
        llm_kwargs_to_use = openai_schema_manager.get_llm_kwargs("ChartSelection")
        partial_vars = {"df_schema": df_schema, "df_head": df_head}
        return llm_kwargs_to_use, partial_vars

    def _post_process(self, response: Dict, *args, **kwargs) -> str:
        """Post process for chart selections which return chart names."""
        chart_names = self._chart_to_use(response)
        return chart_names

    @_log_time
    def run(self, chain_input: str, df: pd.DataFrame = None) -> str:
        """Run chain to get chart type.

        Args:
            chain_input: User question or processed intermediate question if needed.
            df: The dataframe to be analyzed

        Returns:
            Chart type string.

        """
        return super().run(chain_input=chain_input, df=df)

    @staticmethod
    def _get_df_info(df: pd.DataFrame) -> Tuple[str, str]:
        """Get the dataframe schema and head info as string."""
        formatted_pairs = [f"{col_name}: {dtype}" for col_name, dtype in df.dtypes.items()]
        schema_string = "\n".join(formatted_pairs)

        return schema_string, df.head().to_markdown()

    @staticmethod
    def _chart_to_use(load_args) -> str:
        """Get Chart name as string or list of chart names as string."""
        # TODO list of chart name str is for multiple charts to be enabled later
        chart_name = load_args.get("chart_type")
        if isinstance(chart_name, str):
            return chart_name
        else:
            return ",".join(chart_name)


if __name__ == "__main__":
    import plotly.express as px

    from vizro_ai.chains._llm_models import _get_llm_model

    llm_to_use = _get_llm_model()

    df = px.data.gapminder()

    get_chart = GetChartSelection(llm=llm_to_use)
    target_chart = get_chart.run(df=df, chain_input="choose a best chart for describe the composition")
    print(target_chart)  # noqa: T201
