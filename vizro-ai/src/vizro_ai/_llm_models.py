from contextlib import suppress
from typing import Dict, Optional, Union

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_mistralai import ChatMistralAI
except ImportError:
    ChatMistralAI = None

SUPPORTED_MODELS = {
    "OpenAI": [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "gpt-4o",
        "gpt-4o-mini",
    ],
    "Anthropic": [
        "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    "Mistral": ["mistral-large-latest", "open-mistral-nemo", "codestral-latest"],
}

DEFAULT_WRAPPER_MAP: Dict[str, BaseChatModel] = {
    "OpenAI": ChatOpenAI,
    "Anthropic": ChatAnthropic,
    "Mistral": ChatMistralAI,
}

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0

model_to_vendor = {model: key for key, models in SUPPORTED_MODELS.items() for model in models}


def _get_llm_model(model: Optional[Union[BaseChatModel, str]] = None) -> BaseChatModel:
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

    if isinstance(model, BaseChatModel):
        return model

    if isinstance(model, str):
        if any(model in model_list for model_list in SUPPORTED_MODELS.values()):
            vendor = model_to_vendor[model]
            if DEFAULT_WRAPPER_MAP.get(vendor) is None:
                raise ValueError(f"Additional library to support {vendor} models is not installed.")
            return DEFAULT_WRAPPER_MAP.get(vendor)(model_name=model, temperature=DEFAULT_TEMPERATURE)

    raise ValueError(
        f"Model {model} not found! List of available model can be found at https://vizro.readthedocs.io/projects/vizro-ai/en/latest/pages/user-guides/customize-vizro-ai/#supported-models"
    )


def _get_model_name(model: BaseChatModel) -> str:
    methods = [
        lambda: model.model_name,  # OpenAI models
        lambda: model.model,  # Anthropic models
    ]

    for method in methods:
        with suppress(AttributeError):
            return method()

    raise ValueError("Model name could not be retrieved")


if __name__ == "__main__":
    llm_chat_openai = _get_llm_model(model="gpt-3.5-turbo")
    print(repr(llm_chat_openai))  # noqa: T201
    print(llm_chat_openai.model_name)  # noqa: T201
