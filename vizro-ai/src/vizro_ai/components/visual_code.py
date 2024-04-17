"""Visual Code Component."""

from typing import Dict, Tuple

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field

from vizro_ai.chains._chain_utils import _log_time
from vizro_ai.chains._llm_models import LLM_MODELS
from vizro_ai.components import VizroAiComponentBase
from vizro_ai.schema_manager import SchemaManager

# 1. Define schema
openai_schema_manager = SchemaManager()


@openai_schema_manager.register
class VizroCode(BaseModel):
    """Plotly code per user request that is suitable for chart types for given data."""

    visual_code: str = Field(..., description="code snippet for plot visuals using plotly")


# 2. Define prompt
visual_code_prompt = (
    "Context: You are working with a pandas dataframe in Python. The name of the dataframe is `df`."
    "Instructions: Given the code snippet {df_code}, generate Plotly visualization code to produce a {chart_types} "
    "chart that addresses user query: {input}. "
    "Please ensure the Plotly code aligns with the provided DataFrame details."
)


# 3. Define Component
class GetVisualCode(VizroAiComponentBase):
    """Get Visual code.

    Attributes
        prompt (str): Prompt visual code.

    """

    prompt: str = visual_code_prompt

    def __init__(self, llm: LLM_MODELS):
        """Initialization of Chart Selection components.

        Args:
            llm: LLM model wrapped with Langchain wrapper

        """
        super().__init__(llm)

    def _pre_process(self, chart_types: str, df_code: str, *args, **kwargs) -> Tuple[Dict, Dict]:
        """Preprocess for visual code.

        It should return llm_kwargs and partial_vars_map.
        """
        llm_kwargs_to_use = openai_schema_manager.get_llm_kwargs("VizroCode")
        partial_vars_map = {"chart_types": chart_types, "df_code": df_code}

        return llm_kwargs_to_use, partial_vars_map

    def _post_process(self, response: Dict, df_code: str, *args, **kwargs) -> str:
        """Post process for visual code.

        Insert df code and clean up with vizro import.
        """
        code_snippet = self._add_df_string(response.get("visual_code"), df_code)
        return self._clean_visual_code(code_snippet)

    @_log_time
    def run(self, chain_input: str, df_code: str, chart_types: str) -> str:
        """Run chain to get visual code.

        Args:
            chain_input: User input or intermediate question if needed.
            df_code: Code snippet of dataframe.
            chart_types: Chart types.

        Returns:
            Visual code snippet.

        """
        return super().run(chain_input=chain_input, df_code=df_code, chart_types=chart_types)

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
    import plotly.express as px

    from vizro_ai.chains._llm_models import _get_llm_model

    llm_to_use = _get_llm_model()
    df = px.data.gapminder()

    # df_code output from df craft:
    df_code = """import pandas as pd
df = df.groupby('continent')['gdpPercap'].sum().reset_index(name='total_gdpPercap')"""
    test_visual_code = GetVisualCode(llm=llm_to_use)

    res = test_visual_code.run(
        chain_input="choose a best chart for describe the composition of gdp in continent, "
        "and horizontal line for avg gdp",
        chart_types="bar",
        df_code=df_code,
    )
    print(res)  # noqa: T201
