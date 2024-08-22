"""Custom Chart Component."""

import logging
from typing import Dict, Tuple

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field

from langchain_core.language_models.chat_models import BaseChatModel

from vizro_ai.chains._chain_utils import _log_time
from vizro_ai.plot.components import VizroAIComponentBase
from vizro_ai.plot.schema_manager import SchemaManager

logger = logging.getLogger(__name__)

# 1. Define schema
openai_schema_manager = SchemaManager()


@openai_schema_manager.register
class CustomChart(BaseModel):
    """Plotly code per user request that is suitable for chart type for given data."""

    custom_chart_code: str = Field(..., description="Modified and decorated code snippet to allow use in dashboards")


# 2. Define prompt
custom_chart_prompt = """
Your task is to correctly wrap the provided code as instructed. IMPORTANT: Do not mock the data.

Instruction:
1. You wrap the entire chart code into function called '{chart_name}' that takes a single optional arg called
data_frame and returns only the fig object.
For example, if chart_name = "iris_chart", the function should be `def iris_chart(data_frame):` as first line.
2. You ensure that the above function only returns the plotly fig object,
and that the variables are renamed such that all data is derived from 'data_frame'.
3. Leave all imports as is above that function, and do NOT add anything else.

Please modify the following code:
{input}

"""


class GetCustomChart(VizroAIComponentBase):
    # TODO Explore if it is possible to create CustomChart without LLM
    """Get custom chart code.

    Attributes
        prompt (str): Prompt custom chart code.

    """

    prompt: str = custom_chart_prompt

    def __init__(self, llm: BaseChatModel):
        """Initialization of custom chart components.

        Args:
            llm: LLM model wrapped with Langchain wrapper

        """
        super().__init__(llm)

    def _pre_process(self, chart_name: str = "custom_chart", *args, **kwargs) -> Tuple[Dict, Dict]:
        """Preprocess for custom chart.

        It should return llm_kwargs and partial_vars_map.
        """
        llm_kwargs_to_use = openai_schema_manager.get_llm_kwargs("CustomChart")
        partial_vars_map = {"chart_name": chart_name}

        return llm_kwargs_to_use, partial_vars_map

    def _post_process(self, response: Dict, chart_name: str = "custom_chart", *args, **kwargs) -> str:
        """Post process for visual code.

        Insert df code and clean up with vizro import.
        """
        custom_chart_code = response.get("custom_chart_code")
        return self._add_capture_code(custom_chart_code, chart_name)

    @_log_time
    def run(self, chain_input: str, chart_name: str = "custom_chart") -> str:
        """Run chain to get custom chart code.

        Args:
            chain_input: Chain input, undecorated visual code.
            chart_name: Chart name.

        Returns:
            Custom chart snippet.

        """
        return super().run(chain_input=chain_input, chart_name=chart_name)

    @staticmethod
    def _add_capture_code(code_string: str, chart_name: str) -> str:
        """Add df code after last import line."""
        lines = code_string.lstrip().split("\n")
        lines.insert(0, "from vizro.models.types import capture")
        try:
            custom_chart_line = max([idx for idx, line in enumerate(lines) if line.startswith(f"def {chart_name}")])
        except ValueError:
            raise ValueError(f"def {chart_name} is not added correctly by the LLM. Try again.")
        lines.insert(custom_chart_line, "@capture('graph')")
        lines.append(f"\nfig = {chart_name}(data_frame=df)")
        return "\n".join(lines)


if __name__ == "__main__":
    import vizro.plotly.express as px

    from vizro_ai._llm_models import _get_llm_model

    llm_to_use = _get_llm_model()

    df = px.data.gapminder()
    outcome_visual_tool = """
    import vizro.plotly.express as px
    import pandas as pd

    df = df.groupby('continent')['gdpPercap'].sum().reset_index().rename(columns={'gdpPercap': 'total_gdp'})
    fig = px.bar(df, x='continent', y='total_gdp', color='continent', title='Composition of GDP in Continents')
    fig.add_hline(y=df['total_gdp'].mean(), line_dash='dash', line_color='red', annotation_text='Average GDP')
    fig.show()
    """

    test_custom_chart = GetCustomChart(llm=llm_to_use)

    res = test_custom_chart.run(chain_input=outcome_visual_tool)
    print(res)  # noqa: T201
