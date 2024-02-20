import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import ChatGeneration, Generation
from langchain.schema.messages import AIMessage

from vizro_ai.chains._llm_models import LLM_MODELS

logger = logging.getLogger(__name__)


class VizroBaseChain(ABC):
    """Abstract method for base chain."""

    @abstractmethod
    def _construct_prompt(self):
        """Construct the prompt from partial variables and input."""
        pass

    @abstractmethod
    def _custom_parse(self, result):
        """Parse the output."""
        pass

    @abstractmethod
    def execute_chain(self, input_str: str):
        """Execute the LLMChain and get the response."""
        pass


class FunctionCallChain(VizroBaseChain, ABC):
    """LLM Chain with Function Calling."""

    def __init__(  # noqa: PLR0913
        self,
        llm: LLM_MODELS,
        raw_prompt: str,
        partial_vars_map: Optional[Dict[Any, Any]] = None,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        verbose: bool = True,
    ):
        self.llm = llm
        self.raw_prompt = raw_prompt
        self.partial_vars_map = partial_vars_map
        self.llm_kwargs = llm_kwargs
        self.verbose = verbose
        self._chain = None

    def _construct_prompt(self, raw_prompt, partial_vars_map) -> str:
        """Construct the prompt from partial variables input."""
        prompt = PromptTemplate(input_variables=["input"], template=raw_prompt, partial_variables=partial_vars_map)

        vars_set = set(re.findall(r"\{([^}]*)\}", raw_prompt))
        vars_set -= {"input"}

        partial_vars_input = partial_vars_map.keys()
        if partial_vars_input != vars_set:
            different_vars = partial_vars_input ^ vars_set
            logging.warning(
                f"Partial variables input is different from required partial variables in prompt, "
                f"{different_vars} missing"
            )

        prompt.partial_variables = partial_vars_map
        return prompt

    @staticmethod
    def _custom_parse(result) -> Dict[str, Any]:
        """Extract arguments from a list of chat generations.

        It retrieves the arguments embedded within the message and returns them as a dictionary.
        """
        element = result[0]
        if isinstance(element, ChatGeneration):
            if not isinstance(element.message, AIMessage):
                raise TypeError(
                    f"Expected element.message to be of type AIMessage, " f"but got {type(element.message)}"
                )
            args_str = element.message.additional_kwargs.get("function_call", {}).get("arguments", "{}")
            # Remove trailing commas before a closing brace
            args_str = re.sub(r",\s*}", "}", args_str)
            return json.loads(args_str, strict=False)
        # TODO delete when ChatGeneration can be supported for fake llm in langchain
        # fake_llm does not support ChatGeneration, only support Generation
        # For testing, we need to adapt for testing
        elif isinstance(element, Generation):
            return json.loads(element.text, strict=False)

    @property
    def chain(self) -> LLMChain:
        """LLMChain instance."""
        prompt = self._construct_prompt(self.raw_prompt, self.partial_vars_map)
        self.llm_kwargs = self.llm_kwargs or {}
        self._chain = LLMChain(llm=self.llm, prompt=prompt, verbose=self.verbose, llm_kwargs=self.llm_kwargs)
        return self._chain

    def execute_chain(self, input_str: str) -> Dict[str, Any]:
        """Execute chain.

        Args:
            input_str: user question as input string.

        Returns:
            args as a dictionary

        """
        raw_ans = self.chain.generate([{"input": input_str}])
        args = self._custom_parse(raw_ans.generations[0])
        return args


# class NonFunctionCallChain(VizroBaseChain, ABC):
#    TODO implement non function call chain with different execution, prompt, and parser


# class VizroChainRunner:
#     # TODO add cache here in runner class if we need cache
