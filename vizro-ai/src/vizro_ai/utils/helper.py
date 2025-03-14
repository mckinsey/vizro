"""Helper Functions For Vizro AI."""

import json
from pathlib import Path

import pandas as pd

# Dictionary of general best practices for chart creation
GENERAL_CHART_BEST_PRACTICES = {
    "color_usage": """
    - Default Vizro colors apply automatically if no colors are specified
    - If custom colors are needed, select from Vizro palette via `fig.layout.template.layout.colorway`
    - No hard-coded colors, background colors, or plotly color palettes/scales/sequences
    - Exception: Only when visual vocabulary or user explicitly requests specific colors
    """,
    # "data_aggregation": "When using px.bar or px.line charts,
    # aggregate the data appropriately rather than plotting raw values.",
    # "density_heatmap": "For px.density_heatmap, use its built-in 'histfunc' parameter for aggregation
    # rather than pre-aggregating the data.",
    # Add more general best practices here as needed
}


def _get_df_info(df: pd.DataFrame, n_sample: int = 5) -> tuple[str, str]:
    """Get the dataframe schema and head info as string."""
    formatted_pairs = [f"{col_name}: {dtype}" for col_name, dtype in df.dtypes.items()]
    schema_string = "\n".join(formatted_pairs)
    return schema_string, df.sample(n_sample, replace=True, random_state=19).to_markdown()


class DebugFailure(Exception):
    """Debug Failure."""

    pass


def get_vivivo_code_templates() -> dict[str, str]:
    """Extract the code templates from visual vocabulary JSON.

    Returns:
        Dictionary mapping chart type names to their code templates.

    Raises:
        FileNotFoundError: If the visual_vocabulary.json file doesn't exist.
        ValueError: If the JSON structure is invalid or missing expected keys.
    """
    json_path = Path(__file__).parent.parent / "visual_vocabulary.json"
    if not json_path.exists():
        raise FileNotFoundError(f"Visual vocabulary file not found at {json_path}")

    with open(json_path) as f:
        vocabulary_data = json.load(f)

    if "chart_groups" not in vocabulary_data:
        raise ValueError("Invalid visual vocabulary JSON: 'chart_groups' key is missing")

    templates = {}
    for group_name, group_data in vocabulary_data.get("chart_groups", {}).items():
        if "charts" not in group_data:
            raise ValueError(f"Invalid visual vocabulary JSON: 'charts' key is missing in group '{group_name}'")

        for chart in group_data.get("charts", []):
            chart_type = chart.get("chart_name", "")
            example_code = chart.get("example_code", "")

            if not chart_type:
                raise ValueError(
                    f"Invalid visual vocabulary JSON: 'chart_name' missing in chart in group '{group_name}'"
                )

            if not example_code:
                raise ValueError(f"Invalid visual vocabulary JSON: 'example_code' missing for chart '{chart_type}'")

            templates[chart_type] = example_code

    return templates


def _get_vivivo_chart_type_list() -> list[str]:
    """Get a list of all available chart types from the visual vocabulary.

    Returns:
        List of all chart types available in the visual vocabulary.
    """
    templates = get_vivivo_code_templates()
    return list(templates.keys())


def _get_augment_info(chart_type: str, chart_code: str, user_input: str) -> str:
    """Get augmentated prompt to improve chart code with best practices.

    This function takes a chart type, code and user input and returns a formatted string containing:
    1. The original user request
    2. Best practice implementation examples for the specific chart type (if available)
    3. General best practices that apply to all chart types
    4. Instructions for improving the code while maintaining required structure

    Args:
        chart_type: The type of chart (e.g. "scatter", "bar", etc.)
        chart_code: The current chart code implementation to be improved
        user_input: The original user request

    Returns:
        Augmentated prompt containing best practices and instructions for improving the chart code
    """
    code_template = get_vivivo_code_templates()
    if chart_type not in code_template:
        best_practices = None
    else:
        best_practices = code_template[chart_type]

    general_practices_text = "\n".join([f"- {key}: {value}" for key, value in GENERAL_CHART_BEST_PRACTICES.items()])

    vivivo_best_practices_text = f"""
    Follow a STEP-BY-STEP approach:
       a. First, understand the current code.
       b. Study the best practice implementation below thoroughly.
        - Understand what the key operations are and why they are used.
        - Pay close attention to the styling and layout of the chart.
       c. Restructure the code to match the best practice patterns
        - Remove any color choices, unless it's suggested in the best practices.
        - Assess the feasibility of adopting the best practice implementation
            (e.g. whether the data schema is suitable).

    Below is the Vizro best practice implementation for {chart_type} charts.
    FOLLOW THIS PATTERN CLOSELY:
    {best_practices}
    """
    vivivo_best_practices = vivivo_best_practices_text if best_practices else ""

    return f"""
    You are an expert Plotly and Vizro developer tasked with improving the chart code
    so that it is more visually optimal and adheres to Vizro's best practices.

    Original request: {user_input}

    IMPORTANT: Your response must follow the exact same pydantic model structure as before.
    The chart_code field MUST:
    1. Keep the function name as 'custom_chart'
    2. Keep the same parameter signature (data_frame)
    3. Do not include imports in the chart_code field
    4. Use only the provided data_frame parameter - no hardcoded data
    5. Ensure the function always returns a plotly figure object

    {vivivo_best_practices}

    Here is your current code to improve:
    {chart_code}

    GENERAL BEST PRACTICES FOR ALL CHARTS:
    {general_practices_text}
    """
