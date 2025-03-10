"""Helper Functions For Vizro AI."""

import pandas as pd
from vizro_visual_vocabulary import get_code_templates

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


# def _get_code_templates() -> dict[str, str]:
#     """Get code templates using the vizro_visual_vocabulary package.

#     Returns:
#         Dictionary mapping chart types to their example code.
#     """
#     return vv_get_code_templates()


# def create_chart_type_enum() -> type[Enum]:
#     """Create a dynamic Enum from the available chart types using vizro_visual_vocabulary."""
#     return vv_create_chart_type_enum()


def _get_df_info(df: pd.DataFrame, n_sample: int = 5) -> tuple[str, str]:
    """Get the dataframe schema and head info as string."""
    formatted_pairs = [f"{col_name}: {dtype}" for col_name, dtype in df.dtypes.items()]
    schema_string = "\n".join(formatted_pairs)
    return schema_string, df.sample(n_sample, replace=True, random_state=19).to_markdown()


class DebugFailure(Exception):
    """Debug Failure."""

    pass


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
    4. Do not include imports in the chart_code field
    5. Use only the provided data_frame parameter - no hardcoded data
    6. Ensure the function always returns a plotly figure object

    {vivivo_best_practices}

    Here is your current code to improve:
    {chart_code}

    GENERAL BEST PRACTICES FOR ALL CHARTS:
    {general_practices_text}
    """
