"""Pipeline Manager."""

from langchain_core.language_models.chat_models import BaseChatModel
from vizro_ai.vizro_ai_charts.components import GetChartSelection, GetCustomChart, GetDataFrameCraft, GetVisualCode
from vizro_ai.vizro_ai_charts.task_pipeline._pipeline import Pipeline


class PipelineManager:
    """Task pipeline manager."""

    def __init__(self, llm: BaseChatModel = None):
        """Initialize the Pipeline Manager.

        Args:
            llm: Large language Model.

        """
        self.llm = llm

    @property
    def chart_type_pipeline(self):
        """Target chart types pipeline."""
        pipeline = Pipeline(self.llm)
        pipeline.add(GetChartSelection, input_keys=["df", "chain_input"], output_key="chart_types")
        return pipeline

    @property
    def plot_pipeline(self):
        """Plot pipeline."""
        pipeline = Pipeline(self.llm)
        pipeline.add(GetDataFrameCraft, input_keys=["df", "chain_input"], output_key="df_code")
        pipeline.add(GetVisualCode, input_keys=["chain_input", "chart_types", "df_code"], output_key="chain_input")
        pipeline.add(GetCustomChart, input_keys=["chain_input"], output_key="custom_chart_code")
        return pipeline
