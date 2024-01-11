from typing import Any, Callable, Dict


class Pipeline:
    def __init__(self, stages):
        self.stages = stages
        self.components_instances = {}

    def _lazy_get_component(self, component_class: Any) -> Any:  # TODO configure component_class type
        """Lazy initialization of components."""
        if component_class not in self.components_instances:
            self.components_instances[component_class] = component_class(llm=self.llm_to_use)
        return self.components_instances[component_class]

        # target_chart = self._lazy_get_component(GetChartSelection).run(df=df, chain_input=user_input)

    def execute(self, df, user_input):
        context = {'df': df, 'user_input': user_input}
        for stage in self.stages:
            result = stage.run(**context)
            context[stage.__class__.__name__.lower()] = result

# class Pipeline:
#     def __init__(self, executor: Callable):
#         self.operations = []
#         self.executor = executor
#
#     def add(self, component_class: Any):
#         self.operations.append((component_class))
#         return self
#
#     def execute(self, input_data: Dict) -> Dict:
#         for component_class, kwargs in self.operations:
#             output = self.executor(component_class, **kwargs, **input_data)
#             input_data.update(output)
#         return input_data
