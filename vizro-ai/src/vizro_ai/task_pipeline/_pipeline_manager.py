"""Pipeline Manager."""

from vizro_ai.chains._llm_models import LLM_MODELS
from vizro_ai.components import GetChartSelection, GetCustomChart, GetDataFrameCraft, GetVisualCode
from vizro_ai.task_pipeline._pipeline import Pipeline


class PipelineManager:
    """Task pipeline manager."""

    def __init__(self, llm: LLM_MODELS = None):
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
