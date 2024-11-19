import pytest


@pytest.fixture
def get_test_name(request):
    return request.node.name
