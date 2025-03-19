"""Tests for helper functions in vizro_ai.utils.helper."""

import json
from unittest.mock import mock_open, patch

import pytest

from vizro_ai.utils.helper import _get_augment_info, _get_vivivo_chart_type_list, get_vivivo_code_templates


class TestGetAugmentInfo:
    """Tests for the _get_augment_info function."""

    def test_known_chart_type(self, mock_code_templates):
        """Test that _get_augment_info correctly formats augmentation info for known chart types."""
        with patch("vizro_ai.utils.helper.get_vivivo_code_templates", return_value=mock_code_templates):
            chart_type = "scatter"
            chart_code = "def custom_chart(data_frame):\n    return px.scatter(data_frame, x='col1', y='col2')"
            user_input = "Create a scatter plot"

            result = _get_augment_info(chart_type, chart_code, user_input)

            assert chart_type in result
            assert chart_code in result
            assert user_input in result
            assert "FOLLOW THIS PATTERN CLOSELY" in result
            assert mock_code_templates[chart_type] in result
            assert "GENERAL BEST PRACTICES FOR ALL CHARTS" in result

    def test_unknown_chart_type(self, mock_code_templates):
        """Test that _get_augment_info handles chart types not found in templates."""
        with patch("vizro_ai.utils.helper.get_vivivo_code_templates", return_value=mock_code_templates):
            chart_type = "unknown_chart_type"
            chart_code = "def custom_chart(data_frame):\n    return px.line(data_frame, x='col1', y='col2')"
            user_input = "Create an unknown chart"

            result = _get_augment_info(chart_type, chart_code, user_input)

            assert chart_type not in result
            assert user_input in result
            assert chart_code in result
            assert "FOLLOW THIS PATTERN CLOSELY" not in result
            assert "GENERAL BEST PRACTICES FOR ALL CHARTS" in result


class TestGetCodeTemplates:
    """Tests for the get_vivivo_code_templates function."""

    def test_valid_json(self):
        """Test that get_vivivo_code_templates correctly extracts templates from valid JSON."""
        # Create mock JSON content
        mock_json_content = {
            "chart_groups": {
                "group1": {
                    "charts": [
                        {"chart_name": "scatter", "example_code": "example scatter code"},
                        {"chart_name": "line", "example_code": "example line code"},
                    ]
                },
                "group2": {
                    "charts": [
                        {"chart_name": "bar", "example_code": "example bar code"},
                        {"chart_name": "pie", "example_code": "example pie code"},
                    ]
                },
            }
        }

        with (
            patch("builtins.open", mock_open(read_data=json.dumps(mock_json_content))),
            patch("pathlib.Path.exists", return_value=True),
        ):
            templates = get_vivivo_code_templates()

            assert len(templates) == 4
            assert templates["scatter"] == "example scatter code"
            assert templates["line"] == "example line code"
            assert templates["bar"] == "example bar code"
            assert templates["pie"] == "example pie code"

    def test_file_not_exists(self):
        """Test that get_vivivo_code_templates raises FileNotFoundError when JSON file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Visual vocabulary file not found"):
                get_vivivo_code_templates()

    def test_invalid_json_structure_missing_chart_groups(self):
        """Test that get_vivivo_code_templates raises ValueError when JSON is missing chart_groups."""
        mock_json_content = {"other_key": "value"}

        with (
            patch("builtins.open", mock_open(read_data=json.dumps(mock_json_content))),
            patch("pathlib.Path.exists", return_value=True),
        ):
            with pytest.raises(ValueError, match="'chart_groups' key is missing"):
                get_vivivo_code_templates()

    def test_invalid_json_structure_missing_charts(self):
        """Test that get_vivivo_code_templates raises ValueError when JSON is missing charts."""
        mock_json_content = {"chart_groups": {"group1": {"other_key": "value"}}}

        with (
            patch("builtins.open", mock_open(read_data=json.dumps(mock_json_content))),
            patch("pathlib.Path.exists", return_value=True),
        ):
            with pytest.raises(ValueError, match="'charts' key is missing in group"):
                get_vivivo_code_templates()

    def test_invalid_json_structure_missing_chart_name(self):
        """Test that get_vivivo_code_templates raises ValueError when a chart is missing a name."""
        mock_json_content = {
            "chart_groups": {
                "group1": {
                    "charts": [
                        {"example_code": "example code"},
                    ]
                }
            }
        }

        with (
            patch("builtins.open", mock_open(read_data=json.dumps(mock_json_content))),
            patch("pathlib.Path.exists", return_value=True),
        ):
            with pytest.raises(ValueError, match="'chart_name' missing in chart"):
                get_vivivo_code_templates()

    def test_invalid_json_structure_missing_example_code(self):
        """Test that get_vivivo_code_templates raises ValueError when a chart is missing example code."""
        mock_json_content = {
            "chart_groups": {
                "group1": {
                    "charts": [
                        {"chart_name": "scatter"},
                    ]
                }
            }
        }

        with (
            patch("builtins.open", mock_open(read_data=json.dumps(mock_json_content))),
            patch("pathlib.Path.exists", return_value=True),
        ):
            with pytest.raises(ValueError, match="'example_code' missing for chart"):
                get_vivivo_code_templates()


class TestGetVivivoChartTypeList:
    """Tests for the _get_vivivo_chart_type_list function."""

    def test_returns_list_of_chart_types(self):
        """Test that _get_vivivo_chart_type_list returns a list of chart types from templates."""
        mock_templates = {
            "scatter": "example scatter code",
            "bar": "example bar code",
            "line-chart": "example line chart code",
            "pie": "example pie code",
        }

        with patch("vizro_ai.utils.helper.get_vivivo_code_templates", return_value=mock_templates):
            chart_types = _get_vivivo_chart_type_list()

            assert isinstance(chart_types, list)
            assert sorted(chart_types) == sorted(["scatter", "bar", "line-chart", "pie"])
            assert len(chart_types) == 4
