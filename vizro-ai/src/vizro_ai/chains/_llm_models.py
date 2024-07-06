from contextlib import suppress
from typing import Dict, Optional, Union

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None


SUPPORTED_MODELS = {
    "OpenAI": [
        "gpt-4-0613",
        "gpt-3.5-turbo-1106",
        "gpt-4-1106-preview",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo",
        "gpt-4-turbo",
        "gpt-4o",
    ],
    "Anthropic": [
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229",
    ],
}

DEFAULT_WRAPPER_MAP: Dict[str, BaseChatModel] = {"OpenAI": ChatOpenAI, "Anthropic": ChatAnthropic}
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0

model_to_vendor = {model: key for key, models in SUPPORTED_MODELS.items() for model in models}


def _get_llm_model(model: Optional[Union[ChatOpenAI, str]] = None) -> BaseChatModel:
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
                raise ValueError(f"Addtitional library to support {vendor} models is not installed.")
            return DEFAULT_WRAPPER_MAP.get(vendor)(model_name=model, temperature=DEFAULT_TEMPERATURE)

    raise ValueError(
        f"Model {model} not found! List of available model can be found at https://vizro.readthedocs.io/projects/vizro-ai/en/latest/pages/explanation/faq/#which-llms-are-supported-by-vizro-ai"
    )


def _get_model_name(model):
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
