import vizro.models as vm
from vizro_ai.dashboard.nodes._model import _get_structured_output


def test_get_structured_output(component_description, fake_llm):
    structured_output = _get_structured_output(
        query=component_description, llm_model=fake_llm, result_model=vm.Card, df_info=None
    )
    assert structured_output.dict(exclude={"id": True}) == vm.Card(text="this is a card", href="").dict(
        exclude={"id": True}
    )
