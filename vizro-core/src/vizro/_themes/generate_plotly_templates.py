"""Generates Plotly JSON templates for the dark and light themes."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

from plotly import graph_objects as go
from plotly.utils import PlotlyJSONEncoder

from vizro._themes._colors import get_colors
from vizro._themes._common_template import create_template_common

THEMES_FOLDER = Path(__file__).parent
CSS_PATH = THEMES_FOLDER.parent / "static/css/vizro-bootstrap.min.css"
VARIABLES = ["--bs-primary", "--bs-secondary", "--bs-tertiary-color", "--bs-border-color", "--bs-body-bg"]


def _extract_last_two_occurrences(variable: str, css_content: str) -> tuple[Optional[str], Optional[str]]:
    """Extracts the last two occurrences of a variable from the CSS content.

    Within the `vizro-bootstrap.min.css` file, variables appear multiple times: initially from the default Bootstrap
    values, followed by the dark theme, and lastly the light theme. We are interested in the final two occurrences,
    as these represent the values for our dark and light themes.
    """
    matches = re.findall(rf"{variable}:\s*([^;]+);", css_content)
    if len(matches) >= 2:  # noqa: PLR2004
        return matches[-2], matches[-1]
    return None, None


def extract_bs_variables_from_css(variables: list[str], css_content: str) -> tuple[dict[str, str], dict[str, str]]:
    """Extract the last two occurrences for each variable in the CSS file."""
    extracted_dark = {}
    extracted_light = {}

    for variable in variables:
        dark_value, light_value = _extract_last_two_occurrences(variable, css_content)
        cleaned_variable = variable.replace("--", "").upper()
        if dark_value and light_value:
            extracted_dark[cleaned_variable] = dark_value
            extracted_light[cleaned_variable] = light_value

    return extracted_dark, extracted_light


def generate_json_template(extracted_values: dict[str, str]) -> go.layout.Template:
    """Generates the Plotly JSON chart template."""
    FONT_COLOR_PRIMARY = extracted_values["BS-PRIMARY"]
    BG_COLOR = extracted_values["BS-BODY-BG"]
    FONT_COLOR_SECONDARY = extracted_values["BS-SECONDARY"]
    GRID_COLOR = extracted_values["BS-BORDER-COLOR"]
    AXIS_COLOR = extracted_values["BS-TERTIARY-COLOR"]

    # Apply common values
    COLORS = get_colors()
    template = create_template_common()
    layout = template.layout
    layout.update(
        annotationdefaults_font_color=FONT_COLOR_PRIMARY,
        coloraxis_colorbar_tickcolor=AXIS_COLOR,
        coloraxis_colorbar_tickfont_color=FONT_COLOR_SECONDARY,
        coloraxis_colorbar_title_font_color=FONT_COLOR_SECONDARY,
        font_color=FONT_COLOR_PRIMARY,
        geo_bgcolor=BG_COLOR,
        geo_lakecolor=BG_COLOR,
        geo_landcolor=BG_COLOR,
        legend_font_color=FONT_COLOR_PRIMARY,
        legend_title_font_color=FONT_COLOR_PRIMARY,
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        polar_angularaxis_gridcolor=GRID_COLOR,
        polar_angularaxis_linecolor=AXIS_COLOR,
        polar_bgcolor=BG_COLOR,
        polar_radialaxis_gridcolor=GRID_COLOR,
        polar_radialaxis_linecolor=AXIS_COLOR,
        ternary_aaxis_gridcolor=GRID_COLOR,
        ternary_aaxis_linecolor=AXIS_COLOR,
        ternary_baxis_gridcolor=GRID_COLOR,
        ternary_baxis_linecolor=AXIS_COLOR,
        ternary_bgcolor=BG_COLOR,
        ternary_caxis_gridcolor=GRID_COLOR,
        ternary_caxis_linecolor=AXIS_COLOR,
        title_font_color=FONT_COLOR_PRIMARY,
        xaxis_gridcolor=GRID_COLOR,
        xaxis_linecolor=AXIS_COLOR,
        xaxis_tickcolor=AXIS_COLOR,
        xaxis_tickfont_color=FONT_COLOR_SECONDARY,
        xaxis_title_font_color=FONT_COLOR_PRIMARY,
        yaxis_gridcolor=GRID_COLOR,
        yaxis_linecolor=AXIS_COLOR,
        yaxis_tickcolor=AXIS_COLOR,
        yaxis_tickfont_color=FONT_COLOR_SECONDARY,
        yaxis_title_font_color=FONT_COLOR_PRIMARY,
    )
    template.data.bar = [go.Bar(marker_line_color=BG_COLOR)]
    template.data.waterfall = [
        go.Waterfall(
            decreasing={"marker": {"color": COLORS["DISCRETE_10"][1]}},
            increasing={"marker": {"color": COLORS["DISCRETE_10"][0]}},
            totals={"marker": {"color": "grey"}},
            textfont_color=FONT_COLOR_PRIMARY,
            textposition="outside",
            connector={"line": {"color": AXIS_COLOR, "width": 1}},
        )
    ]
    return template


if __name__ == "__main__":
    extracted_dark, extracted_light = extract_bs_variables_from_css(VARIABLES, CSS_PATH.read_text())
    template_dark = generate_json_template(extracted_dark)
    template_light = generate_json_template(extracted_light)

    parser = argparse.ArgumentParser(description="Generate JSON plotly templates.")
    parser.add_argument("--check", help="check plotly templates are up to date", action="store_true")
    args = parser.parse_args()

    for generated_template, file_name in zip([template_dark, template_light], ["vizro_dark.json", "vizro_light.json"]):
        existing_template_path = Path(f"{THEMES_FOLDER}/{file_name}")
        existing_template = json.loads(existing_template_path.read_text())
        if args.check:
            if existing_template != generated_template.to_plotly_json():
                sys.exit(f"Chart template `{file_name}` is out of date. Run `hatch run templates` to update it.")
            print(f"Chart template `{file_name}` is up to date 🎉")  # noqa: T201
        else:
            existing_template_path.write_text(json.dumps(generated_template, indent=4, cls=PlotlyJSONEncoder))
