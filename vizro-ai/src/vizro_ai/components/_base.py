from abc import ABC, abstractmethod
from typing import Dict, Tuple, Union

from vizro_ai.chains import FunctionCallChain
from vizro_ai.chains._llm_models import LLM_MODELS


class VizroAiComponentBase(ABC):
    """Abstract Base Class that represents a blueprint for Vizro-AI components.

    Attributes
        prompt (str): Prompt for specific components.

    Public Methods:
        run: Run the Chain with preprocess and postprocess to get cleaned up response.

    Private Methods:
        _pre_process: A helper method for LLMChain input vars preprocess.
        _post_process: Another helper method for LLMChain output postprocess.

    """

    prompt: str = "default prompt place holder"

    def __init__(self, llm: LLM_MODELS):
        """Initialize Vizro-AI base component.

        Args:
            llm: LLM model wrapped with Langchain wrapper.

        """
        self.llm = llm

    @abstractmethod
    def _pre_process(self, *args, **kwargs) -> Tuple[Dict, Dict]:
        """Preprocess steps of getting the required input of chain.

        Usually it should handle llm_kwargs_to_use and partial_vars_map.
        """
        pass

    @abstractmethod
    def _post_process(self, response: Dict, *args, **kwargs) -> Union[str, tuple[str, str]]:
        """Post process steps of getting the desired output from the chain."""
        pass

    def run(self, chain_input: str, *args, **kwargs) -> str:
        """Run the LLMChain with preprocess and postprocess to get cleaned up response.

        Args:
            chain_input: A string containing the user's input/query.
            args: Argument list for additional positional arguments.
            kwargs: Arbitrary keyword arguments for additional configurations.

        Returns:
           The return type will be depending on post process.

        """
        llm_kwargs_to_use, partial_vars = self._pre_process(*args, **kwargs)

        function_call_chain = FunctionCallChain(
            llm=self.llm, raw_prompt=self.prompt, partial_vars_map=partial_vars, llm_kwargs=llm_kwargs_to_use
        )

        response = function_call_chain.execute_chain(input_str=chain_input)

        return self._post_process(response, *args, **kwargs)
