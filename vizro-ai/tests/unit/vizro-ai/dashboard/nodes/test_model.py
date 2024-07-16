import vizro.models as vm
from vizro_ai.dashboard._pydantic_output import _get_pydantic_output


def test_get_pydantic_output(component_description, fake_llm):
    structured_output = _get_pydantic_output(
        query=component_description, llm_model=fake_llm, result_model=vm.Card, df_info=None
    )
    assert structured_output.dict(exclude={"id": True}) == vm.Card(text="this is a card", href="").dict(
        exclude={"id": True}
    )
