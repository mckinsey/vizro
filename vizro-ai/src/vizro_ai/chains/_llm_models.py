from typing import Dict, Union

from langchain_openai import ChatOpenAI

# TODO add new wrappers in if new model support is added
LLM_MODELS = Union[ChatOpenAI]

# TODO constant of model inventory, can be converted to yaml and link to docs
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
    },
}


class ModelConstructor:
    """Manages available Language Learning Models (LLMs).

    Provides methods to fetch LLM details and instantiate appropriate wrappers.
    """

    def get_llm_model(self, model=None) -> LLM_MODELS:
        """Fetches and initializes an instance of the LLM.

        Returns
            The initialized instance of the LLM.

        Raises
            ValueError: If the model name is not found.

        """
        if isinstance(model, str):
            if model in PREDEFINED_MODELS:
                model_dict = PREDEFINED_MODELS.get(model)
                return model_dict["wrapper"](model_name=model, temperature=0)
            else:
                ValueError(f"Model {model} not found!")
        elif isinstance(model, ChatOpenAI):
            return model
        return ChatOpenAI(model_name="gpt-3.5-turbo-0613", temperature=0)


if __name__ == "__main__":
    model_manager = ModelConstructor()
    llm_chat_openai = model_manager.get_llm_model()
