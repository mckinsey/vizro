from typing import Dict, Optional, Union

from langchain_openai import ChatOpenAI

# TODO add new wrappers in if new model support is added
LLM_MODELS = Union[ChatOpenAI]

# TODO constant of model inventory, can be converted to yaml and link to docs
PREDEFINED_MODELS: Dict[str, Dict[str, Union[int, LLM_MODELS]]] = {
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
    "gpt-3.5-turbo-0125": {
        "max_tokens": 16385,
        "wrapper": ChatOpenAI,
    },
    "gpt-3.5-turbo": {
        "max_tokens": 16385,
        "wrapper": ChatOpenAI,
    },
    "gpt-4-turbo": {
        "max_tokens": 128000,
        "wrapper": ChatOpenAI,
    },
}

DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0


def _get_llm_model(model: Optional[Union[ChatOpenAI, str]] = None) -> LLM_MODELS:
    """Fetches and initializes an instance of the LLM.

    Args:
        model: Model instance or model name.

    Returns:
        The initialized instance of the LLM.

    Raises:
        ValueError: If the provided model string does not match any pre-defined model

    """
    if not model:
        return ChatOpenAI(model_name=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE)
    if isinstance(model, ChatOpenAI):
        return model
    if isinstance(model, str) and model in PREDEFINED_MODELS:
        return PREDEFINED_MODELS.get(model)["wrapper"](model_name=model, temperature=DEFAULT_TEMPERATURE)
    raise ValueError(
        f"Model {model} not found! List of available model can be found at https://vizro.readthedocs.io/projects/vizro-ai/en/latest/pages/explanation/faq/#which-llms-are-supported-by-vizro-ai"
    )


if __name__ == "__main__":
    llm_chat_openai = _get_llm_model()
