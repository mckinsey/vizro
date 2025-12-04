"""
Analyze color-related arguments in all 35 Plotly Express functions.

This script was originally used to work out the `ChartType` definitions used in charts.py but is not needed at runtime.
"""

import inspect
import plotly.express as px

# All 35 functions (excluding mapbox and imshow)
PX_FUNCTIONS = [
    # 2D Cartesian
    "scatter",
    "line",
    "area",
    "bar",
    "timeline",
    "histogram",
    "ecdf",
    "violin",
    "box",
    "strip",
    # Hierarchical
    "pie",
    "sunburst",
    "treemap",
    "icicle",
    "funnel",
    "funnel_area",
    # Statistical
    "density_contour",
    "density_heatmap",
    # Geographic
    "scatter_geo",
    "line_geo",
    "choropleth",
    # Map
    "scatter_map",
    "line_map",
    "choropleth_map",
    "density_map",
    # Polar
    "scatter_polar",
    "line_polar",
    "bar_polar",
    # 3D
    "scatter_3d",
    "line_3d",
    # Ternary
    "scatter_ternary",
    "line_ternary",
    # Special
    "scatter_matrix",
    "parallel_coordinates",
    "parallel_categories",
]

# Color-related parameters to check
COLOR_PARAMS = [
    "color",
    "color_discrete_sequence",
    "color_discrete_map",
    "color_continuous_scale",
    "color_continuous_midpoint",
    "range_color",
]


def analyze_function(px_name):
    """Analyze color-related arguments for a px function."""
    try:
        px_fn = getattr(px, px_name)
        sig = inspect.signature(px_fn)
        params = sig.parameters

        result = {"px_name": px_name}
        for param in COLOR_PARAMS:
            result[param] = param in params

        return result
    except Exception as e:
        return {"px_name": px_name, "error": str(e)}


# Analyze all functions
results = []
for px_name in PX_FUNCTIONS:
    results.append(analyze_function(px_name))

# Group by category
categories = {
    "2D Cartesian": ["scatter", "line", "area", "bar", "timeline", "histogram", "ecdf", "violin", "box", "strip"],
    "Hierarchical": ["pie", "sunburst", "treemap", "icicle", "funnel", "funnel_area"],
    "Statistical": ["density_contour", "density_heatmap"],
    "Geographic": ["scatter_geo", "line_geo", "choropleth"],
    "Map": ["scatter_map", "line_map", "choropleth_map", "density_map"],
    "Polar": ["scatter_polar", "line_polar", "bar_polar"],
    "3D": ["scatter_3d", "line_3d"],
    "Ternary": ["scatter_ternary", "line_ternary"],
    "Special": ["scatter_matrix", "parallel_coordinates", "parallel_categories"],
}

# Generate markdown output
markdown_lines = []
markdown_lines.append("# Plotly Express Color Arguments Analysis\n")
markdown_lines.append("Analysis of color-related arguments in all 35 Plotly Express functions.\n")
markdown_lines.append("| Category | Function | `color` | Discrete Args | Continuous Args |")
markdown_lines.append("|----------|----------|---------|---------------|-----------------|")

for category, func_names in categories.items():
    for px_name in func_names:
        result = next((r for r in results if r["px_name"] == px_name), None)
        if result and "error" not in result:
            has_color = "✓" if result.get("color") else "✗"
            has_discrete = "✓" if (result.get("color_discrete_sequence") or result.get("color_discrete_map")) else "✗"
            has_continuous = (
                "✓"
                if (
                    result.get("color_continuous_scale")
                    or result.get("color_continuous_midpoint")
                    or result.get("range_color")
                )
                else "✗"
            )

            markdown_lines.append(f"| {category} | `{px_name}` | {has_color} | {has_discrete} | {has_continuous} |")
        else:
            error_msg = result.get("error", "Not found") if result else "Not found"
            markdown_lines.append(f"| {category} | `{px_name}` | ERROR | {error_msg} | |")

markdown_lines.append("\n## Legend\n")
markdown_lines.append("- **`color`**: Has `color` parameter")
markdown_lines.append("- **Discrete Args**: Has `color_discrete_sequence` or `color_discrete_map`")
markdown_lines.append(
    "- **Continuous Args**: Has `color_continuous_scale`, `color_continuous_midpoint`, or `range_color`"
)

# Write to file
output_file = "color_args_analysis.md"
with open(output_file, "w") as f:
    f.write("\n".join(markdown_lines))

print(f"Markdown table saved to {output_file}")
