import pytest
import vizro.models as vm
from langchain_core.messages import HumanMessage


@pytest.fixture
def component_description():
    return "This is a card"


@pytest.fixture
def expected_card():
    return vm.Card(text="this is a card")


@pytest.fixture
def query():
    return "I need a page with one card saying: Simple card."


@pytest.fixture
def message_output_valid():
    return {"message": [HumanMessage(content="I need a page with one card saying: Simple card.")], "df_info": None}


@pytest.fixture
def message_output_error():
    return {
        "message": [HumanMessage(content="I need a page with one card saying: Simple card.")],
        "df_info": None,
        "validation_error": "ValidationError",
    }
