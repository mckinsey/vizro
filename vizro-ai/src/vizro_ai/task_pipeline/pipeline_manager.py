from vizro_ai.task_pipeline.pipeline import Pipeline

from vizro_ai.components import (
    GetChartSelection,
    GetCodeExplanation,
    GetCustomChart,
    GetDataFrameCraft,
    GetDebugger,
    GetVisualCode,
)


class PipelineManager:
    def __init__(self, llm=None):
        self.llm = llm

    def create_plot_pipeline(self):
        """ Create and return the plot pipeline. """
        pipeline = Pipeline(self.llm)
        pipeline.add(GetChartSelection, input_keys=['df', 'chain_input'], output_key='chart_types')
        pipeline.add(GetDataFrameCraft, input_keys=['df', 'chain_input'], output_key='df_code')
        pipeline.add(GetVisualCode, input_keys=['chain_input', 'chart_types', 'df_code'], output_key='chain_input')
        pipeline.add(GetCustomChart, input_keys=['chain_input'], output_key='custom_chart_code')
        # Add more components as needed
        return pipeline
