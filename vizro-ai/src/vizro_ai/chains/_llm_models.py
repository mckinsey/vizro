from typing import Callable, Dict, List, Union

from langchain_openai import ChatOpenAI

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field

# TODO add new wrappers in if new model support is added
LLM_MODELS = Union[ChatOpenAI]

# TODO constant of model inventory, can be converted to yaml and link to docs
# temperature 0 redefine
# PREDEFINED_MODELS: List[Dict[str, any]] = [
#     {
#         "name": "gpt-3.5-turbo-0613",
#         "max_tokens": 4096,
#         "wrapper": ChatOpenAI,
#     },
#     {
#         "name": "gpt-4-0613",
#         "max_tokens": 8192,
#         "wrapper": ChatOpenAI,
#     },
#     {
#         "name": "gpt-3.5-turbo-1106",
#         "max_tokens": 16385,
#         "wrapper": ChatOpenAI,
#     },
#     {
#         "name": "gpt-4-1106-preview",
#         "max_tokens": 128000,
#         "wrapper": ChatOpenAI,
#     },
# ]
PREDEFINED_MODELS: Dict[str, Dict[str, any]] = {
    "gpt-3.5-turbo-0613": {
        "max_tokens": 4096,
        "wrapper": ChatOpenAI,
    },
    "gpt-4-0613": {
        "max_tokens": 8192,
        "wrapper": ChatOpenAI,
    },
    "gpt-3.5-turbo-1106": {
        "max_tokens": 16385,
        "wrapper": ChatOpenAI,
    },
    "gpt-4-1106-preview": {
        "max_tokens": 128000,
        "wrapper": ChatOpenAI,
    }
}


class LLM(BaseModel):
    """Represents a Language Learning Model (LLM).

    Attributes
        name (str): The name of the LLM.
        max_tokens (int): The maximum number of tokens that the LLM can handle.
        wrapper (callable): The langchain function used to instantiate the model.

    """

    name: str
    max_tokens: int
    wrapper: Callable = Field(..., description="The langchain function used to instantiate the model.")


class ModelConstructor:
    """Manages available Language Learning Models (LLMs).

    Provides methods to fetch LLM details and instantiate appropriate wrappers.
    """

    models: Dict[str, LLM]

    # def __init__(self):
    #     """Initializes the model manager with a set of predefined LLMs."""
    #     self.models = {model["name"]: LLM(**model) for model in PREDEFINED_MODELS}

    def get_llm_model(self, model) -> LLM_MODELS:
        """Fetches and initializes an instance of the LLM.

        Args:
            model_name (str): The name of the LLM.
            temperature (int, optional): A parameter for the wrapper. Defaults to 0.

        Returns:
            The initialized instance of the LLM.

        Raises:
            ValueError: If the model name is not found.

        """
        if model:
            if model.model_name not in PREDEFINED_MODELS:
                raise ValueError(f"Model {model.model_name} not found!")
            else:
                return model
        return ChatOpenAI(model_name="gpt-3.5-turbo-0613", temperature=0)


if __name__ == "__main__":
    model_manager = ModelConstructor()
    llm_chat_openai = model_manager.get_llm_model()
