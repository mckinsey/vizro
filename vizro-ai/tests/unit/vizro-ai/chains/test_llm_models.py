import pytest
from vizro_ai.chains._llm_models import _get_llm_model


@pytest.mark.parametrize(
    "model_name",
    [
        "gpt-3.5-turbo-1"  # invalid model name
        "gpt-3.5-turbo-instruct"  # model not supported
    ],
)
def test_get_llm_model_invalid_model_name(model_name):
    with pytest.raises(ValueError, match=f"Model {model_name} not found!"):
        _get_llm_model(model_name)
