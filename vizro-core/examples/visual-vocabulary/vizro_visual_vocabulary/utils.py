"""Utilities for accessing chart examples."""

from enum import Enum
from pathlib import Path


def get_code_templates() -> dict[str, str]:
    """Extract the code templates from example charts.

    Returns:
        Dictionary mapping chart type names to their code templates.
    """
    templates = {}
    examples_dir = Path(__file__).parent / "pages" / "examples"

    for py_file in examples_dir.glob("*.py"):
        # Skip __init__.py and utilities
        if py_file.stem.startswith("_"):
            continue

        # Extract the chart type from filename
        chart_type = py_file.stem.replace("_", "-")

        with open(py_file) as f:
            content = f.read()

        templates[chart_type] = content

    return templates


def create_chart_type_enum() -> Enum:
    """Create an Enum of all available chart types.

    Returns:
        Enum with all chart types available in the visual vocabulary.
    """
    templates = get_code_templates()

    ChartType = Enum("ChartType", {k.replace("-", "_").upper(): k for k in templates.keys()})

    return ChartType
