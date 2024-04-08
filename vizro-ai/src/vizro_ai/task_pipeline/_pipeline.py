"""Task Pipeline."""

from typing import Any, Dict, List, Optional

from vizro_ai.chains._llm_models import LLM_MODELS


class Pipeline:
    """A pipeline to manage the flow of tasks in a sequence."""

    def __init__(self, llm: LLM_MODELS):
        """Initialize the Pipeline.

        Args:
            llm: The LLM instance to be used by components in the pipeline.

        """
        self.llm = llm
        self.components = []
        self.components_instances = {}

    def add(self, component_class, input_keys: Optional[List[str]] = None, output_key: Optional[str] = None):
        """Add a component class to the pipeline along with its input and output specifications.

        Args:
            component_class: The class of the component to be added to the pipeline.
            input_keys: The keys or identifiers for the inputs that this component expects.
                    These should match the output keys of previous components in the pipeline, if applicable.
            output_key: The key or identifier for the output that this component will produce.
                    This can be used as an input key for subsequent components.

        """
        self.components.append((component_class, input_keys, output_key))

    def run(self, initial_args: Dict[str, Any]):
        """Execute the pipeline with the provided initial args.

        Args:
            initial_args: Initial arguments that need to be passed for pipeline.

        Returns:
            Output of the last stage in pipeline.

        """
        context = initial_args
        output = None
        for component_class, input_keys, output_key in self.components:
            component = self._lazy_get_component(component_class)
            kwargs = {key: context[key] for key in input_keys} if input_keys else {}
            output = component.run(**kwargs)
            # TODO extend to multiple output keys and output type
            if output_key:
                context[output_key] = output
        return output

    def _lazy_get_component(self, component_class: Any) -> Any:  # TODO configure component_class type
        """Lazy initialization of components."""
        if component_class not in self.components_instances:
            self.components_instances[component_class] = component_class(llm=self.llm)
        return self.components_instances[component_class]
