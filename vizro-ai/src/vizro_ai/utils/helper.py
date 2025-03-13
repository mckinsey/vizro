"""Helper Functions For Vizro AI."""

import json
from enum import Enum
from pathlib import Path

import pandas as pd

# Dictionary of general best practices for chart creation
GENERAL_CHART_BEST_PRACTICES = {
    "color_usage": """
    1. AVOID using hard-coded colors.
    2. AVOID using plotly color palettes, color scales, or color sequence

    If you must use colors:
    Use the default Vizro color palette by accessing `fig.layout.template.layout.colorway`.

    When to make exceptions:
    Only if it's suggested by the visual vocabulary or the user request.
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


def get_code_templates() -> dict[str, str]:
    """Extract the code templates from visual vocabulary JSON.

    Returns:
        Dictionary mapping chart type names to their code templates.
    """
    # Find the path to the JSON file
    json_path = Path(__file__).parent.parent / "visual_vocabulary.json"

    # Ensure the file exists
    if not json_path.exists():
        return {}

    # Load the JSON data
    with open(json_path) as f:
        vocabulary_data = json.load(f)

    templates = {}

    # Extract code examples from the JSON
    for group_data in vocabulary_data.get("chart_groups", {}).values():
        for chart in group_data.get("charts", []):
            chart_type = chart.get("chart_name", "")
            example_code = chart.get("example_code", "")

            if chart_type and example_code:
                templates[chart_type] = example_code

    return templates


def _create_chart_type_enum() -> Enum:
    """Create an Enum of all available chart types.

    Returns:
        Enum with all chart types available in the visual vocabulary.
    """
    templates = get_code_templates()

    # Create the enum from the templates dictionary
    ChartType = Enum("ChartType", {k.replace("-", "_").upper(): k for k in templates.keys()})

    return ChartType


def _get_augment_info(chart_type: str, chart_code: str, user_input: str) -> str:
    """Get the augment info."""
    code_template = get_code_templates()
    if chart_type not in code_template:
        best_practices = None
    else:
        best_practices = code_template[chart_type]

    # Create a section for general best practices
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
