"""Example script demonstrating how to use get_model_schema from vizro_mcp.

This script shows how to retrieve JSON schemas for various Vizro models,
which is useful for understanding the expected structure of dashboard configurations.

Usage:
    python examples/schema_example.py
"""

import json

from vizro_mcp import get_model_schema, get_vizro_version


def print_schema(model_name: str) -> None:
    """Print the schema for a given Vizro model."""
    print(f"\n{'=' * 60}")
    print(f"Model: {model_name}")
    print("=" * 60)

    result = get_model_schema(model_name)

    if not result.json_schema:
        print("  Status: Not found or deprecated")
        print(f"  Info: {result.additional_info}")
        return

    print(f"  Properties: {list(result.json_schema.get('properties', {}).keys())}")
    print(f"  Required: {result.json_schema.get('required', [])}")

    if result.additional_info:
        print(f"  Note: {result.additional_info[:100]}...")

    # Print full schema (formatted)
    print("\n  Full Schema:")
    print("  " + json.dumps(result.json_schema, indent=2).replace("\n", "\n  "))


def main():
    print(f"Vizro MCP Schema Explorer (Vizro version: {get_vizro_version()})")

    # Common models to explore
    models = [
        "Dashboard",
        "Page",
        "Graph",
        "Card",
        "Filter",
        "Parameter",
        "AgGrid",
        "Figure",
        "Grid",
        "Flex",
        # Deprecated models
        "Layout",
        # Non-existent model
        "NonExistentModel",
    ]

    for model in models:
        print_schema(model)


if __name__ == "__main__":
    main()
