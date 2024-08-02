import vizro.models as vm
from vizro_ai.dashboard._pydantic_output import _create_message_content, _create_prompt_template, _get_pydantic_model


def test_get_pydantic_output(component_description, fake_llm):
    pydantic_output = _get_pydantic_model(
        query=component_description, llm_model=fake_llm, response_model=vm.Card, df_info=None
    )
    assert pydantic_output.dict(exclude={"id": True}) == vm.Card(text="this is a card", href="").dict(
        exclude={"id": True}
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
