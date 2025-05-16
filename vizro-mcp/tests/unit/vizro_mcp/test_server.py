"""Unit tests for Vizro MCP server tools."""

from typing import Any

import pytest
import vizro.models as vm
from vizro_mcp._schemas import (
    AgGridEnhanced,
    ContainerSimplified,
    DashboardSimplified,
    FilterSimplified,
    GraphEnhanced,
    PageSimplified,
    ParameterSimplified,
    TabsSimplified,
)
from vizro_mcp._utils import IRIS
from vizro_mcp.server import (
    DFMetaData,
    ValidationResults,
    get_model_json_schema,
    validate_chart_code,
    validate_model_config,
)


@pytest.fixture
def iris_metadata() -> DFMetaData:
    """Fixture for Iris dataset metadata."""
    return IRIS


@pytest.fixture
def valid_dashboard_config() -> dict[str, Any]:
    """Fixture for a valid dashboard configuration."""
    return {
        "title": "Test Dashboard",
        "pages": [
            {
                "id": "test_page",
                "title": "Test Page",
                "components": [
                    {
                        "id": "test_card",
                        "type": "card",
                        "text": "Test content",
                    }
                ],
            }
        ],
    }


@pytest.fixture
def dashboard_config_validation_result() -> ValidationResults:
    """Fixture for a dashboard configuration validation result."""
    return ValidationResults(
        valid=True,
        message="Configuration is valid for Dashboard!",
        python_code="""############ Imports ##############
import vizro.models as vm
from vizro import Vizro
import pandas as pd
from vizro.managers import data_manager


########### Model code ############
model = vm.Dashboard(
    pages=[
        vm.Page(
            id="test_page",
            components=[vm.Card(id="test_card", type="card", text="Test content")],
            title="Test Page",
        )
    ],
    title="Test Dashboard",
)

Vizro().build(model).run()""",
        pycafe_url="https://py.cafe/snippet/vizro/v1?c=H4sIAFLGG...",
        browser_opened=False,
    )


@pytest.fixture
def graph_dashboard_config() -> dict[str, Any]:
    """Fixture for a dashboard configuration with a scatter graph."""
    return {
        "title": "Graph Dashboard",
        "pages": [
            {
                "id": "graph_page",
                "title": "Scatter Graph Page",
                "components": [
                    {
                        "id": "scatter_graph",
                        "type": "graph",
                        "figure": {
                            "_target_": "scatter",
                            "data_frame": "iris_data",
                            "x": "sepal_length",
                            "y": "sepal_width",
                            "color": "species",
                            "title": "Iris Scatter Plot",
                        },
                    }
                ],
            }
        ],
    }


@pytest.fixture
def graph_dashboard_validation_result() -> ValidationResults:
    """Fixture for a dashboard configuration with graph validation result."""
    return ValidationResults(
        valid=True,
        message="Configuration is valid for Dashboard!",
        python_code="""############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
import pandas as pd
from vizro.managers import data_manager


####### Data Manager Settings #####
data_manager["iris_data"] = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/iris-id.csv")

########### Model code ############
model = vm.Dashboard(
    pages=[
        vm.Page(
            id="graph_page",
            components=[
                vm.Graph(
                    id="scatter_graph",
                    type="graph",
                    figure=px.scatter(
                        data_frame="iris_data",
                        x="sepal_length",
                        y="sepal_width",
                        color="species",
                        title="Iris Scatter Plot",
                    ),
                )
            ],
            title="Scatter Graph Page",
        )
    ],
    title="Graph Dashboard",
)

Vizro().build(model).run()""",
        pycafe_url="https://py.cafe/snippet/vizro/v1?c=example-hash",
        browser_opened=False,
    )


@pytest.fixture
def valid_chart_plan() -> dict[str, Any]:
    """Fixture for a valid chart plan."""
    return {
        "chart_type": "scatter",
        "imports": ["import pandas as pd", "import plotly.express as px"],
        "chart_code": """def custom_chart(data_frame):
        return px.scatter(data_frame, x="sepal_length", y="sepal_width", color="species", title="Iris Scatter Plot")""",
    }


@pytest.fixture
def invalid_chart_plan() -> dict[str, Any]:
    """Fixture for an invalid chart plan."""
    return {
        "chart_type": "scatter",
        "imports": ["import pandas as pd", "import plotly.express as px"],
        "chart_code": """def scatter_chart(data_frame):
        return px.scatter(data_frame, x="sepal_length", y="sepal_width", color="species", title="Iris Scatter Plot")""",
    }


@pytest.fixture
def chart_plan_validation_result() -> ValidationResults:
    """Fixture for a chart plan validation result."""
    return ValidationResults(
        valid=True,
        message="Chart only dashboard created successfully!",
        python_code="""@capture('graph')
def custom_chart(data_frame):
        return px.scatter(data_frame, x="sepal_length", y="sepal_width", color="species", title="Iris Scatter Plot")""",
        pycafe_url="https://py.cafe/snippet/vizro/v1?c=...",
        browser_opened=False,
    )


class TestValidateModelConfig:
    """Tests for the validate_model_config tool."""

    def test_successful_validation(
        self, valid_dashboard_config: dict[str, Any], dashboard_config_validation_result: ValidationResults
    ) -> None:
        """Test successful validation of a dashboard configuration."""
        result = validate_model_config(dashboard_config=valid_dashboard_config, data_infos=[], auto_open=False)

        # Compare everything but the pycafe_url
        assert result.valid == dashboard_config_validation_result.valid
        assert result.message == dashboard_config_validation_result.message
        assert result.python_code == dashboard_config_validation_result.python_code
        assert result.browser_opened == dashboard_config_validation_result.browser_opened

        # For the URL, just check it has the right format
        assert result.pycafe_url is not None
        assert result.pycafe_url.startswith("https://py.cafe/snippet/vizro/v1?c=")

    def test_graph_dashboard_validation(
        self,
        graph_dashboard_config: dict[str, Any],
        graph_dashboard_validation_result: ValidationResults,
        iris_metadata: DFMetaData,
    ) -> None:
        """Test validation of a dashboard with a scatter graph component."""
        result = validate_model_config(
            dashboard_config=graph_dashboard_config, data_infos=[iris_metadata], auto_open=False
        )

        # Compare everything but the pycafe_url
        assert result.valid == graph_dashboard_validation_result.valid
        assert result.message == graph_dashboard_validation_result.message
        assert result.python_code == graph_dashboard_validation_result.python_code
        assert result.browser_opened == graph_dashboard_validation_result.browser_opened

        # For the URL, just check it has the right format
        assert result.pycafe_url is not None
        assert result.pycafe_url.startswith("https://py.cafe/snippet/vizro/v1?c=")

    def test_validation_error(self, valid_dashboard_config: dict[str, Any], iris_metadata: DFMetaData) -> None:
        """Test validation error for an invalid dashboard configuration."""
        # Create an invalid config by removing a required field
        invalid_config = valid_dashboard_config.copy()
        invalid_config["titles"] = invalid_config.pop("title")

        result = validate_model_config(dashboard_config=invalid_config, data_infos=[iris_metadata], auto_open=False)

        assert result.valid is False
        assert "Validation Error: 1 validation error for Dashboard" in result.message
        assert result.python_code == ""
        assert result.pycafe_url is None
        assert result.browser_opened is False


class TestValidateChartCode:
    """Tests for the validate_chart_code tool."""

    def test_successful_validation(
        self,
        valid_chart_plan: dict[str, Any],
        iris_metadata: DFMetaData,
        chart_plan_validation_result: ValidationResults,
    ) -> None:
        """Test successful validation of chart code."""
        result = validate_chart_code(chart_config=valid_chart_plan, data_info=iris_metadata, auto_open=False)

        # Compare everything but the pycafe_url
        assert result.valid == chart_plan_validation_result.valid
        assert result.message == chart_plan_validation_result.message
        assert result.python_code == chart_plan_validation_result.python_code
        assert result.browser_opened == chart_plan_validation_result.browser_opened

        # For the URL, just check it has the right format
        assert result.pycafe_url is not None
        assert result.pycafe_url.startswith("https://py.cafe/snippet/vizro/v1?c=")

    def test_validation_error(
        self,
        invalid_chart_plan: dict[str, Any],
        iris_metadata: DFMetaData,
    ) -> None:
        """Test validation error for an invalid chart plan."""
        result = validate_chart_code(chart_config=invalid_chart_plan, data_info=iris_metadata, auto_open=False)

        assert result.valid is False
        assert result.python_code == ""
        assert result.pycafe_url is None
        assert result.browser_opened is False
        assert "Validation Error: 1 validation error for ChartPlan" in result.message


class TestGetModelJsonSchema:
    """Tests for the get_model_json_schema tool."""

    @pytest.mark.parametrize(
        "model_name, model_class",
        [
            # Standard models from vizro.models
            ("Card", vm.Card),
            # Simplified models from vizro_mcp._schemas
            ("Dashboard", DashboardSimplified),
            ("Page", PageSimplified),
            ("Container", ContainerSimplified),
            ("Tabs", TabsSimplified),
            ("Filter", FilterSimplified),
            ("Parameter", ParameterSimplified),
            # Enhanced models from vizro_mcp._schemas
            ("Graph", GraphEnhanced),
            ("AgGrid", AgGridEnhanced),
            ("Table", AgGridEnhanced),
        ],
    )
    def test_model_json_schema(self, model_name: str, model_class: type) -> None:
        """Test getting JSON schema for various models."""
        schema = get_model_json_schema(model_name=model_name)

        # Get the schema directly from the model class
        expected_schema = model_class.model_json_schema()

        # Compare the schemas
        assert schema == expected_schema

    def test_nonexistent_model(self) -> None:
        """Test getting schema for a nonexistent model."""
        schema = get_model_json_schema("NonExistentModel")

        assert isinstance(schema, dict)
        assert "error" in schema
        assert "not found" in schema["error"]
