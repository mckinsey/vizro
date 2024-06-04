"""Chart Type Selection Component."""

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
class CodeExplanation(BaseModel):
    """Explanation text which describes the meaning of given code snippet."""

    business_insights: str = Field(
        ..., description="Detailed explanation or interpretation of business insights of plots"
    )
    code_explanation: str = Field(..., description="an explanation of the python code line by line")


# 2. Define prompt
code_explanation_prompt = (
    "Given user question {input} and answer {code_snippet}, (less than 400 characters),"
    "DO NOT just use one sentence for business insights, give detailed information"
)


# 3. Define Component
class GetCodeExplanation(VizroAiComponentBase):
    """Get Explanation of a code snippet.

    Attributes
        prompt (str): Prompt code explanation.

    """

    prompt: str = code_explanation_prompt

    def __init__(self, llm: LLM_MODELS):
        """Initialization of Code Explanation components.

        Args:
            llm: LLM model wrapped with Langchain wrapper

        """
        super().__init__(llm)

    def _pre_process(self, code_snippet: str, *args, **kwargs) -> Tuple[Dict, Dict]:
        """Preprocess for code explanation.

        It should return llm_kwargs and partial_vars_map for
        """
        llm_kwargs_to_use = openai_schema_manager.get_llm_kwargs("CodeExplanation")
        partial_vars = {"code_snippet": code_snippet}

        return llm_kwargs_to_use, partial_vars

    def _post_process(self, response: Dict, *args, **kwargs) -> tuple[str, str]:
        """Post-process for code explanation which returns text."""
        business_insights = response.get("business_insights")
        code_explanation = self._text_cleanup(response.get("code_explanation"))
        return business_insights, code_explanation

    @_log_time
    def run(self, chain_input: str, code_snippet: str) -> str:
        """Run chain to get code explanation.

        Args:
            chain_input: User question or processed intermediate question if needed.
            code_snippet: The code snippet to be analyzed.

        Returns:
            Code explanation.

        """
        return super().run(chain_input=chain_input, code_snippet=code_snippet)

    @staticmethod
    def _text_cleanup(load_args) -> str:
        """Final cleanup on the explanation."""
        substring = "Plotly Express"
        code_string = load_args.replace(substring, "Plotly Express and Vizro")
        cleaned_code_explanation = (
            f"{code_string}\n<br>**This customized chart can be directly used in a Vizro dashboard.** "
            f"\nClick [custom chart docs](https://vizro.readthedocs.io/en/stable/pages/user_guides/custom_charts/) "
            f"for more information."
        )
        return cleaned_code_explanation


if __name__ == "__main__":
    from vizro_ai.chains._llm_models import _get_llm_model

    llm_to_use = _get_llm_model()

    code_snippet = """
    from vizro.models.types import capture
    import vizro.plotly.express as px
    import pandas as pd

    @capture('graph')
    def custom_chart(data_frame: pd.DataFrame = None):
        if data_frame is None:
            data_frame = pd.DataFrame()
        df = data_frame.groupby('continent')['gdpPercap'].sum().reset_index().rename(columns={'gdpPercap': 'total_gdp'})
        fig = px.bar(df, x='continent', y='total_gdp', color='continent', title='Composition of GDP in Continents')
        fig.add_hline(y=df['total_gdp'].mean(), line_dash='dash', line_color='red', annotation_text='Average GDP')
        return fig

    fig = custom_chart(data_frame=df)
    """

    get_explanation = GetCodeExplanation(llm=llm_to_use)
    business_insights, code_explanation = get_explanation.run(
        chain_input="choose a best chart for describe the composition of gdp in continent, "
        "and horizontal line for avg gdp",
        code_snippet=code_snippet,
    )
    print(business_insights, code_explanation)  # noqa: T201
