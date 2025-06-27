"""Unit tests for Vizro MCP server tools."""

from typing import Any

import pytest
import vizro.models as vm
from vizro_mcp._schemas import (
    AgGridEnhanced,
    ChartPlan,
    GraphEnhanced,
)
from vizro_mcp._utils import IRIS
from vizro_mcp._utils.utils import NoDefsGenerateJsonSchema
from vizro_mcp.server import (
    DFMetaData,
    ValidateResults,
    get_model_json_schema,
    validate_chart_code,
    validate_dashboard_config,
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
def valid_dashboard_config_validation_result() -> ValidateResults:
    """Fixture for a dashboard configuration validation result."""
    return ValidateResults(
        valid=True,
        message="""Configuration is valid for Dashboard! Do not forget to call this tool again after each iteration.
If you are creating an `app.py` file, you MUST use the code from the validation tool, do not modify it, watch out for
differences to previous `app.py`""",
        python_code="""############ Imports ##############
import vizro.models as vm
from vizro import Vizro


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

Vizro().build(model).run()
""",
        pycafe_url="https://py.cafe/snippet/vizro/v1?c=H4sIAFLGG...",
        browser_opened=False,
    )


@pytest.fixture
def valid_graph_dashboard_config() -> dict[str, Any]:
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
                    },
                    {
                        "id": "custom_scatter_graph",
                        "type": "graph",
                        "figure": {
                            "_target_": "custom_scatter",
                            "data_frame": "iris_data",
                        },
                    },
                ],
            }
        ],
    }


@pytest.fixture
def valid_graph_dashboard_validation_result() -> ValidateResults:
    """Fixture for a dashboard configuration with graph validation result."""
    return ValidateResults(
        valid=True,
        message="""Configuration is valid for Dashboard! Do not forget to call this tool again after each iteration.
If you are creating an `app.py` file, you MUST use the code from the validation tool, do not modify it, watch out for
differences to previous `app.py`""",
        python_code="""############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm
from vizro.models.types import capture
from vizro import Vizro
import pandas as pd
from vizro.managers import data_manager
import vizro.plotly.express as px
from vizro.models.types import capture


####### Function definitions ######
@capture("graph")
def custom_scatter(data_frame):
    return px.scatter(
        data_frame,
        x="sepal_length",
        y="sepal_width",
        color="species",
        title="Iris Scatter Plot",
    )


####### Data Manager Settings #####
data_manager["iris_data"] = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/iris-id.csv"
)

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
                ),
                vm.Graph(
                    id="custom_scatter_graph",
                    type="graph",
                    figure=custom_scatter(data_frame="iris_data"),
                ),
            ],
            title="Scatter Graph Page",
        )
    ],
    title="Graph Dashboard",
)

Vizro().build(model).run()
""",
        pycafe_url="https://py.cafe/snippet/vizro/v1?c=example-hash",
        browser_opened=False,
    )


@pytest.fixture
def valid_chart_plan() -> dict[str, Any]:
    """Fixture for a valid chart plan."""
    return {
        "chart_type": "scatter",
        "chart_name": "custom_scatter",
        "imports": ["import pandas as pd", "import plotly.express as px"],
        "chart_code": """def custom_scatter(data_frame):
        return px.scatter(data_frame, x="sepal_length", y="sepal_width", color="species", title="Iris Scatter Plot")""",
    }


@pytest.fixture
def invalid_chart_plan() -> dict[str, Any]:
    """Fixture for an invalid chart plan."""
    return {
        "chart_type": "scatter",
        "chart_name": "scatter_chart_wrong",
        "imports": ["import pandas as pd", "import plotly.express as px"],
        "chart_code": """def scatter_chart(data_frame):
        return px.scatter(data_frame, x="sepal_length", y="sepal_width", color="species", title="Iris Scatter Plot")""",
    }


@pytest.fixture
def chart_plan_validation_result() -> ValidateResults:
    """Fixture for a chart plan validation result."""
    return ValidateResults(
        valid=True,
        message="Chart only dashboard created successfully!",
        python_code="""@capture('graph')
def custom_scatter(data_frame):
        return px.scatter(data_frame, x="sepal_length", y="sepal_width", color="species", title="Iris Scatter Plot")""",
        pycafe_url="https://py.cafe/snippet/vizro/v1?c=...",
        browser_opened=False,
    )


class TestValidateModelConfig:
    """Tests for the validate_dashboard_config tool."""

    def test_successful_validation(
        self,
        valid_dashboard_config: dict[str, Any],
        valid_dashboard_config_validation_result: ValidateResults,
    ) -> None:
        """Test successful validation of a dashboard configuration."""
        result = validate_dashboard_config(
            dashboard_config=valid_dashboard_config, data_infos=[], custom_charts=[], auto_open=False
        )

        # Compare everything but the pycafe_url
        assert result.valid == valid_dashboard_config_validation_result.valid
        assert result.message == valid_dashboard_config_validation_result.message
        assert result.python_code == valid_dashboard_config_validation_result.python_code
        assert result.browser_opened == valid_dashboard_config_validation_result.browser_opened

        # For the URL, just check it has the right format
        assert result.pycafe_url is not None
        assert result.pycafe_url.startswith("https://py.cafe/snippet/vizro/v1?c=")

    def test_graph_dashboard_validation(
        self,
        valid_graph_dashboard_config: dict[str, Any],
        valid_graph_dashboard_validation_result: ValidateResults,
        iris_metadata: DFMetaData,
        valid_chart_plan: dict[str, Any],
    ) -> None:
        """Test validation of a dashboard with a scatter graph component."""
        result = validate_dashboard_config(
            dashboard_config=valid_graph_dashboard_config,
            data_infos=[iris_metadata],
            auto_open=False,
            custom_charts=[ChartPlan.model_validate(valid_chart_plan)],
        )

        # Compare everything but the pycafe_url
        assert result.valid == valid_graph_dashboard_validation_result.valid
        assert result.message == valid_graph_dashboard_validation_result.message
        assert result.python_code == valid_graph_dashboard_validation_result.python_code
        assert result.browser_opened == valid_graph_dashboard_validation_result.browser_opened

        # For the URL, just check it has the right format
        assert result.pycafe_url is not None
        assert result.pycafe_url.startswith("https://py.cafe/snippet/vizro/v1?c=")

    def test_validation_error(self, valid_dashboard_config: dict[str, Any], iris_metadata: DFMetaData) -> None:
        """Test validation error for an invalid dashboard configuration."""
        # Create an invalid config by removing a required field
        invalid_config = valid_dashboard_config.copy()
        invalid_config["titles"] = invalid_config.pop("title")

        result = validate_dashboard_config(
            dashboard_config=invalid_config, data_infos=[iris_metadata], custom_charts=[], auto_open=False
        )

        assert result.valid is False
        assert "Extra inputs are not permitted" in result.message
        assert result.python_code == ""
        assert result.pycafe_url is None
        assert result.browser_opened is False

    def test_validation_error_missing_custom_chart(
        self, valid_graph_dashboard_config: dict[str, Any], iris_metadata: DFMetaData
    ) -> None:
        """Test validation error for a dashboard configuration with a missing custom chart."""
        result = validate_dashboard_config(
            dashboard_config=valid_graph_dashboard_config, data_infos=[iris_metadata], custom_charts=[], auto_open=False
        )

        assert result.valid is False
        assert "Failed to import function 'custom_scatter' from any of the attempted paths" in result.message


class TestValidateChartCode:
    """Tests for the validate_chart_code tool."""

    def test_successful_validation(
        self,
        valid_chart_plan: dict[str, Any],
        iris_metadata: DFMetaData,
        chart_plan_validation_result: ValidateResults,
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
        "model_name",
        [
            # Standard models from vizro.models
            "Card",
            "Page",
            "Container",
            "Tabs",
            "Filter",
            "Parameter",
            "Dashboard",
        ],
    )
    def test_standard_model_json_schema(self, model_name: str) -> None:
        """Test getting JSON schema for standard models."""
        # Get schema through the get_model_json_schema function
        result = get_model_json_schema(model_name=model_name)
        schema = result.json_schema

        # Get the model class directly from vizro.models
        model_class = getattr(vm, model_name)

        # The schema should be generated using NoDefsGenerateJsonSchema
        expected_schema = model_class.model_json_schema(schema_generator=NoDefsGenerateJsonSchema)

        # Compare the schemas
        assert schema == expected_schema

    @pytest.mark.parametrize(
        "model_name, enhanced_class,additional_info_snippet",
        [
            # Enhanced models from vizro_mcp._schemas
            ("Graph", GraphEnhanced, "This is the plotly express figure to be displayed."),
            ("AgGrid", AgGridEnhanced, "This is the ag-grid figure to be displayed."),
            ("Table", AgGridEnhanced, "This is the ag-grid figure to be displayed."),
        ],
    )
    def test_enhanced_model_json_schema(
        self, model_name: str, enhanced_class: type, additional_info_snippet: str
    ) -> None:
        """Test getting JSON schema for enhanced models."""
        # Get schema through the get_model_json_schema function
        result = get_model_json_schema(model_name=model_name)
        schema = result.json_schema

        # Compare with directly generated schema
        expected_schema = enhanced_class.model_json_schema(schema_generator=NoDefsGenerateJsonSchema)

        # Compare the schemas
        assert schema == expected_schema
        # Check for fixed string to ensure that the schema is correct
        assert additional_info_snippet in schema["properties"]["figure"]["description"]

    def test_nonexistent_model(self) -> None:
        """Test getting schema for a nonexistent model."""
        result = get_model_json_schema("NonExistentModel")

        assert result.additional_info == "Model 'NonExistentModel' not found in vizro.models"
