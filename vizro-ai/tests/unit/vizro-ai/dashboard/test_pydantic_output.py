import pytest
import vizro.models as vm

from vizro_ai.dashboard._pydantic_output import _create_message_content, _create_prompt_template, _get_pydantic_model


def test_get_pydantic_model_valid(component_description, fake_llm, expected_card):
    result = _get_pydantic_model(query=component_description, llm_model=fake_llm, response_model=vm.Card, df_info=None)

    assert result.model_dump(exclude={"id": True}) == expected_card.model_dump(exclude={"id": True})


def test_get_pydantic_model_invalid(component_description, fake_llm_invalid):
    with pytest.raises(ValueError, match="1 validation error for Card"):
        _get_pydantic_model(
            query=component_description, llm_model=fake_llm_invalid, response_model=vm.Card, df_info=None
        )


def test_create_message_content_valid(query, message_output_valid):
    message_content = _create_message_content(query=query, df_info=None)

    assert message_content == message_output_valid


def test_create_message_content_error(query, message_output_error):
    message_content = _create_message_content(query=query, df_info=None, validation_error="ValidationError", retry=True)
    assert message_content == message_output_error


def test_create_prompt_template():
    additional_info = "Pay special attention to the following error: {validation_error}"
    model = _create_prompt_template(additional_info)
    assert additional_info in model.messages[0].prompt.template
