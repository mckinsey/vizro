"""Visual Code Component."""

from typing import Dict, Tuple

import pandas as pd

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field

from langchain_core.language_models.chat_models import BaseChatModel

from vizro_ai.chains._chain_utils import _log_time
from vizro_ai.plot.components import VizroAIComponentBase
from vizro_ai.plot.schema_manager import SchemaManager
from vizro_ai.utils.helper import _get_df_info

# 1. Define schema
openai_schema_manager = SchemaManager()


@openai_schema_manager.register
class VizroCode(BaseModel):
    """Plotly code per user request that is suitable for chart type for given data."""

    visual_code: str = Field(..., description="code snippet for plot visuals using plotly")


# 2. Define prompt
visual_code_prompt = """
Context: You are an AI assistant specialized in data visualization using Python, pandas, and Plotly.

Given:
- A pandas DataFrame named `df`
- DataFrame schema: {df_schema}
- Sample data (first few rows): {df_sample}
- Data preprocessing code: {df_code}
- User's visualization request: {input}
- Requested chart type: {chart_type}

Instructions:
1. Analyze the provided DataFrame information and preprocessing code.
2. Generate Plotly code to create a {chart_type} chart that addresses the user's query: {input}
3. Ensure the visualization accurately represents the data and aligns with the DataFrame structure.
4. Use appropriate Plotly Express functions when possible for simplicity.
5. If custom Plotly Graph Objects are necessary, provide clear explanations.
6. Include axis labels, title, and any other relevant chart components.
7. If color coding or additional visual elements would enhance the chart, incorporate them.

Output:
- Provide the complete Plotly code required to generate the requested visualization.

Note: Ensure all variable names and data references are consistent with the provided DataFrame (`df`).
"""


# 3. Define Component
class GetVisualCode(VizroAIComponentBase):
    """Get Visual code.

    Attributes
        prompt (str): Prompt visual code.

    """

    prompt: str = visual_code_prompt

    def __init__(self, llm: BaseChatModel):
        """Initialization of Chart Selection components.

        Args:
            llm: LLM model wrapped with Langchain wrapper

        """
        super().__init__(llm)

    def _pre_process(self, chart_type: str, df_code: str, df: pd.DataFrame, *args, **kwargs) -> Tuple[Dict, Dict]:
        """Preprocess for visual code.

        It should return llm_kwargs and partial_vars_map.
        """
        llm_kwargs_to_use = openai_schema_manager.get_llm_kwargs("VizroCode")

        df_schema, df_sample = _get_df_info(df)

        partial_vars_map = {
            "chart_type": chart_type,
            "df_code": df_code,
            "df_schema": df_schema,
            "df_sample": df_sample,
        }

        return llm_kwargs_to_use, partial_vars_map

    def _post_process(self, response: Dict, df_code: str, *args, **kwargs) -> str:
        """Post process for visual code.

        Insert df code and clean up with vizro import.
        """
        code_snippet = self._add_df_string(response.get("visual_code"), df_code)
        return self._clean_visual_code(code_snippet)

    @_log_time
    def run(self, chain_input: str, df_code: str, chart_type: str, df: pd.DataFrame = None) -> str:
        """Run chain to get visual code.

        Args:
            chain_input: User input or intermediate question if needed.
            df_code: Code snippet of dataframe.
            chart_type: chart type.
            df: The dataframe for plotting.

        Returns:
            Visual code snippet.

        """
        return super().run(chain_input=chain_input, df_code=df_code, chart_type=chart_type, df=df)

    @staticmethod
    def _add_df_string(code_string: str, df_code: str) -> str:
        """Add df code after last import line."""
        lines = code_string.split("\n")
        last_import_idx = max([idx for idx, line in enumerate(lines) if line.startswith("import")], default=-1)
        lines.insert(last_import_idx + 1, df_code)
        return "\n".join(lines)

    @staticmethod
    def _clean_visual_code(raw_code: str) -> str:
        """Add vizro import."""
        cleaned_code = raw_code.replace("import plotly.express as px", "import vizro.plotly.express as px")
        return cleaned_code


if __name__ == "__main__":
    import vizro.plotly.express as px

    from vizro_ai._llm_models import _get_llm_model

    llm_to_use = _get_llm_model()
    df = px.data.gapminder()

    # df_code output from df craft:
    df_code = """import pandas as pd
df = df.groupby('continent')['gdpPercap'].sum().reset_index(name='total_gdpPercap')"""
    test_visual_code = GetVisualCode(llm=llm_to_use)

    res = test_visual_code.run(
        chain_input="choose a best chart for describe the composition of gdp in continent, "
        "and horizontal line for avg gdp",
        chart_type="bar",
        df_code=df_code,
    )
    print(res)  # noqa: T201
