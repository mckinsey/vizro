"""Dataframe craft Component."""

import logging
import re
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

logger = logging.getLogger(__name__)

# 1. Define schema
openai_schema_manager = SchemaManager()


@openai_schema_manager.register
class DataFrameCraft(BaseModel):
    """Dataframe manipulation code per user request that is suitable for given data."""

    dataframe_code: str = Field(..., description="code snippet for pandas dataframe manipulation")


# 2. Define prompt
dataframe_prompt = """Context: You are working with a pandas DataFrame in Python named df.
DataFrame Details Schema: {df_schema}, Sample Data: {df_head}, User Query: {input}
Instructions: 1.Write code to manipulate the df DataFrame according to the user's query.
2.Do not create any new DataFrames; work only with df.
3.Ensure that any aggregated columns are named appropriately and re-indexed if necessary.
4.If a visualization is implied by the user's query, only write the necessary DataFrame manipulation
code for that visualization. 5.Do not include any plotting code.
6. Produce the code in a line-by-line format, not wrapped inside a function."""


# 3. Define Component
class GetDataFrameCraft(VizroAiComponentBase):
    """Get dataframe code.

    Attributes
        prompt (str): Prompt dataframe wrangling chain.

    """

    prompt: str = dataframe_prompt

    def __init__(self, llm: LLM_MODELS):
        """Initialization of dataframe crafting components.

        Args:
            llm: LLM model wrapped with Langchain wrapper

        """
        super().__init__(llm)

    def _pre_process(self, df: pd.DataFrame, *args, **kwargs) -> Tuple[Dict, Dict]:
        """Preprocess for dataframe tool.

        It should return llm_kwargs and partial_vars_map
        """
        df_schema, df_head = self._get_df_info(df)
        llm_kwargs_to_use = openai_schema_manager.get_llm_kwargs("DataFrameCraft")
        partial_vars_map = {"df_schema": df_schema, "df_head": df_head}

        return llm_kwargs_to_use, partial_vars_map

    def _post_process(self, response: Dict, *args, **kwargs) -> str:
        df_code_snippet = response.get("dataframe_code")
        return self._format_dataframe_string(df_code_snippet)

    @_log_time
    def run(self, chain_input: str, df: pd.DataFrame = None) -> str:
        """Run chain to get dataframe code.

        Args:
            chain_input: User question or processed intermediate question if needed.
            df: The dataframe to be analyzed

        Returns:
            Dataframe code snippet

        """
        return super().run(chain_input, df)

    @staticmethod
    def _get_df_info(df: pd.DataFrame) -> Tuple[str, str]:
        """Get the dataframe schema and head info as string."""
        formatted_pairs = [f"{col_name}: {dtype}" for col_name, dtype in df.dtypes.items()]
        schema_string = "\n".join(formatted_pairs)

        return schema_string, df.head().to_markdown()

    @staticmethod
    def _format_dataframe_string(s: str) -> str:
        """Format the dataframe code snippet string."""
        if "import pandas as pd" not in s:
            s = "import pandas as pd\n" + s

        s = re.sub(r"\.plot\([^)]*\)", "", s)

        lines = s.split("\n")
        code_lines = [line for line in lines if line]

        if not code_lines[-1].startswith("df = "):
            if " = " in code_lines[-1]:
                code_lines[-1] = "df = " + code_lines[-1].split(sep=" = ")[1]
            else:
                code_lines[-1] = "df = " + code_lines[-1]

        reset_string = "" if ".reset_index(" in code_lines[-1] else ".reset_index()"
        code_lines[-1] = code_lines[-1] + reset_string

        s = "\n".join(code_lines)

        return s


if __name__ == "__main__":
    import plotly.express as px

    from vizro_ai.chains._llm_models import _get_llm_model

    llm_to_use = _get_llm_model()
    df = px.data.gapminder()

    test_df_crafter = GetDataFrameCraft(llm=llm_to_use)
    res = test_df_crafter.run(df=df, chain_input="choose a best chart for describe the composition of gdp in continent")
    print(res)  # noqa: T201
