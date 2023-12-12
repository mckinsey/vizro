from typing import Callable, Dict, List, Union

from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel, Field

# TODO add new wrappers in if new model support is added
LLM_MODELS = Union[ChatOpenAI]

# TODO constant of model inventory, can be converted to yaml and link to docs
PREDEFINED_MODELS: List[Dict[str, any]] = [
    {
        "name": "gpt-3.5-turbo-0613",
        "max_tokens": 4096,
        "wrapper": ChatOpenAI,
    },
    {
        "name": "gpt-4-0613",
        "max_tokens": 8192,
        "wrapper": ChatOpenAI,
    },
]


class LLM(BaseModel):
    """Represents a Language Learning Model (LLM).

    Attributes:
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

    def __init__(self):
        """Initializes the model manager with a set of predefined LLMs."""
        self.models = {model["name"]: LLM(**model) for model in PREDEFINED_MODELS}

    def get_llm_model(self, model_name: str, temperature: float = 0) -> LLM_MODELS:
        """Fetches and initializes an instance of the LLM.

        Args:
            model_name (str): The name of the LLM.
            temperature (int, optional): A parameter for the wrapper. Defaults to 0.

        Returns:
            The initialized instance of the LLM.

        Raises:
            ValueError: If the model name is not found.
        """
        model = self.models.get(model_name.lower())
        if model:
            return model.wrapper(model_name=model.name, temperature=temperature)
        else:
            raise ValueError(f"Model {model_name} not found!")


if __name__ == "__main__":
    model_manager = ModelConstructor()
    llm_chat_openai = model_manager.get_llm_model("gpt-3.5-turbo-0613", temperature=0)
