
class Pipeline:
    """A pipeline to manage the flow of tasks in a sequence, with integrated lazy component loading."""

    def __init__(self, llm):
        """
        Initialize the Pipeline with the LLM to use for components.

        Args:
            llm: The LLM instance to be used by components in the pipeline.
        """
        self.llm = llm
        self.components = []
        self.components_instances = {}

    def add(self, component_class, input_keys=None, output_key=None):
        """
        Add a component class to the pipeline along with its input and output specifications.
        """
        self.components.append((component_class, input_keys, output_key))

    def _lazy_get_component(self, component_class):
        """Lazy initialization of components."""
        if component_class not in self.components_instances:
            self.components_instances[component_class] = component_class(llm=self.llm)
        return self.components_instances[component_class]

    def run(self, chain_input, df):
        """
        Execute the pipeline with the provided initial input and dataframe.
        """
        context = {'chain_input': chain_input, 'df': df}
        output = None
        for component_class, input_keys, output_key in self.components:
            component = self._lazy_get_component(component_class)
            args = {key: context[key] for key in input_keys} if input_keys else {}
            output = component.run(**args)
            # TODO consider extend to multiple output keys
            if output_key:
                context[output_key] = output

        return output
