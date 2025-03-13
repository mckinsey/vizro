"""Fixtures specific to the utils module tests."""

import pytest


@pytest.fixture
def mock_code_templates():
    """Mock return value for get_code_templates."""
    return {
        "scatter": (
            "import vizro.plotly.express as px\n\n"
            "iris = px.data.iris()\n\n"
            'fig = px.scatter(iris, x="sepal_width", y="sepal_length", color="species")\n'
        ),
        "bar": 'import vizro.plotly.express as px\n\nfig = px.bar(data_frame, x="category", y="value")\n',
    }
