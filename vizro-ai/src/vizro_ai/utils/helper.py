"""Helper Functions For Vizro AI."""

from enum import Enum
from importlib import resources
from pathlib import Path
from typing import Optional, Type
import pandas as pd
import vizro


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
    # "data_aggregation": "When using px.bar or px.line charts, aggregate the data appropriately rather than plotting raw values.",
    # "density_heatmap": "For px.density_heatmap, use its built-in 'histfunc' parameter for aggregation rather than pre-aggregating the data.",
    # Add more general best practices here as needed
}

def _get_code_templates() -> dict[str, str]:
    """Get code templates from examples directory in vizro package.
    
    Returns:
        Dictionary mapping chart types to their example code.
    """
    code_templates = {}
    
    # Try multiple possible locations for examples
    possible_paths = []
    
    try:
        # 1. First try: Standard repo layout path
        repo_root = Path(__file__).parent.parent.parent.parent.parent  # Navigate up to repo root
        possible_paths.append(repo_root / "vizro-core/examples/visual-vocabulary/pages/examples")
        
        # 2. Second try: Monorepo layout
        monorepo_root = Path(__file__).parent.parent.parent.parent.parent.parent
        possible_paths.append(monorepo_root / "vizro/vizro-core/examples/visual-vocabulary/pages/examples")
        
        # 3. Third try: Check for packaged examples if installed via pip
        if hasattr(vizro, '__file__'):
            vizro_pkg_path = Path(vizro.__file__).parent
            possible_paths.append(vizro_pkg_path / "examples/visual-vocabulary/pages/examples")
        
        # Debug all paths we're checking
        print(f"Searching for examples in these locations:")
        for p in possible_paths:
            print(f"- {p.absolute()}")
        
        # Try each path until we find one that exists
        examples_path = None
        for path in possible_paths:
            if path.exists():
                examples_path = path
                print(f"Found examples at: {examples_path}")
                break
        
        if not examples_path:
            print(f"Warning: Examples directory not found at any of the expected locations")
            # Fall back to hardcoded chart types
            return {}
            
        # Iterate through all .py files in the directory
        for file_path in examples_path.glob("*.py"):
            # Get chart type from filename (without .py extension)
            chart_type = file_path.stem
            
            # Read the file content
            code_content = file_path.read_text()
            code_templates[chart_type] = code_content
            print(f"Loaded template: {chart_type}")
            
    except Exception as e:
        print(f"Warning: Could not load example templates: {e}")
        return {}
    
    return code_templates


def create_chart_type_enum() -> Type[Enum]:
    """Create a dynamic Enum from the available chart types."""
    print("Starting create_chart_type_enum()")
    templates = _get_code_templates()
    
    # Filter out __init__ if present
    chart_types = [k for k in templates.keys() if k != "__init__"]
    print(f"After filtering __init__: {len(chart_types)} chart types")
    
    if not chart_types:
        print("Using fallback chart types since no valid templates were found")
        chart_types = [
            "scatter", "bar", "line", "pie", "histogram"
        ]
    
    # Create enum via dictionary comprehension
    enum_dict = {k.upper(): k for k in chart_types}
    print(f"Created enum_dict with {len(enum_dict)} items")
    
    try:
        # Use functional API to create enum
        print("About to create Enum")
        chart_type_enum = Enum('VisualVocabularyChartType', enum_dict)
        print("Enum created successfully")
        
        # Verify the enum is properly populated
        enum_values = [member.value for member in chart_type_enum]
        print(f"Created enum with {len(enum_values)} values: {enum_values[:10]}...")
        
        return chart_type_enum
    except Exception as e:
        print(f"Error creating enum: {e}")
        # Return a minimal enum as fallback
        return Enum('VisualVocabularyChartType', {'SCATTER': 'scatter', 'BAR': 'bar'})


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
    code_template = _get_code_templates()
    print(code_template.get(chart_type))
    if chart_type not in code_template:
        best_practices = None
    else:
        best_practices = code_template[chart_type]
    
    # Create a section for general best practices
    general_practices_text = "\n".join([f"- {key}: {value}" for key, value in GENERAL_CHART_BEST_PRACTICES.items()])

    vivivo_best_practices_text = f"""
    Follow a STEP-BY-STEP approach:
       a. First, understand the current code
       b. Study the best practice implementation below thoroughly. 
        - Understand what the key operations are and why they are used.
        - Pay close attention to the styling and layout of the chart.
       c. Restructure the code to match the best practice patterns
        - Remove any color choices, unless it's suggested in the best practices.
        - Assess the feasibility of adopting the best practice implementation (e.g. whether the data schema is suitable).
    
    Below is the Vizro best practice implementation for {chart_type} charts.
    FOLLOW THIS PATTERN CLOSELY:
    {best_practices}
    """
    vivivo_best_practices = vivivo_best_practices_text if best_practices else ""
    
    return f"""
    You are an expert Plotly and Vizro developer tasked with improving the chart code so that it is more visually optimal and adheres to Vizro's best practices.
    
    Original request: {user_input}

    IMPORTANT: Your response must follow the exact same pydantic model structure as before.
    The chart_code field MUST:
    1. Keep the function name as 'custom_chart'
    2. Keep the same parameter signature (data_frame)
    4. Do not include imports in the chart_code field
    5. Use only the provided data_frame parameter - no hardcoded data
    6. Ensure the function always returns a plotly figure object
    
    {vivivo_best_practices_text}

    Here is your current code to improve:
    {chart_code}

    GENERAL BEST PRACTICES FOR ALL CHARTS:
    {general_practices_text}
    """
