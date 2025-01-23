import argparse
import json
import re
import sys
from pathlib import Path

from plotly import graph_objects as go
from plotly.utils import PlotlyJSONEncoder

from vizro._themes._color_values import COLORS
from vizro._themes.common_values import create_template_common

THEMES_FOLDER = Path(__file__).resolve().parent
CSS_FILE = THEMES_FOLDER.parent / "static" / "css" / "vizro-bootstrap.min.css"
VARIABLES = ["--bs-primary", "--bs-secondary", "--bs-tertiary-color", "--bs-border-color", "--bs-body-bg"]


def _extract_last_two_occurrences(variable: str, content):
    """Extracts the last two occurrences of a variable from the CSS content.

    Within the `vizro-bootstrap.min.css` file, variables appear multiple times: initially from the default Bootstrap
    values, followed by the dark theme, and lastly the light theme. We are interested in the final two occurrences,
    as these represent the values for our dark and light themes.
    """
    pattern = re.compile(rf"{variable}:\s*([^;]+);")
    matches = pattern.findall(content)
    if len(matches) >= 2:  # noqa: PLR2004
        return matches[-2].strip(), matches[-1].strip()

    return None, None


def extract_bs_variables_from_css_file(variables, css_file_path):
    """Extract the last two occurrences for each variable in the list."""
    extracted_dark = {}
    extracted_light = {}

    with open(css_file_path) as css_file:
        css_content = css_file.read()

    for variable in variables:
        dark_values, light_values = _extract_last_two_occurrences(variable, css_content)
        cleaned_variable = variable.replace("--", "").upper()
        extracted_dark[cleaned_variable] = dark_values
        extracted_light[cleaned_variable] = light_values

    return extracted_dark, extracted_light


def generate_json_template(extracted_values):
    """Generate the Python file content from the extracted values."""
    FONT_COLOR_PRIMARY = extracted_values["BS-PRIMARY"]
    BG_COLOR = extracted_values["BS-BODY-BG"]
    FONT_COLOR_SECONDARY = extracted_values["BS-SECONDARY"]
    GRID_COLOR = extracted_values["BS-BORDER-COLOR"]
    AXIS_COLOR = extracted_values["BS-TERTIARY-COLOR"]

    # Apply common values
    template = create_template_common()
    template.layout.font.color = FONT_COLOR_PRIMARY
    template.layout.title.font.color = FONT_COLOR_PRIMARY
    template.layout.legend.font.color = FONT_COLOR_PRIMARY
    template.layout.legend.title.font.color = FONT_COLOR_PRIMARY
    template.layout.paper_bgcolor = BG_COLOR
    template.layout.plot_bgcolor = BG_COLOR
    template.layout.geo.bgcolor = BG_COLOR
    template.layout.geo.lakecolor = BG_COLOR
    template.layout.geo.landcolor = BG_COLOR
    template.layout.polar.bgcolor = BG_COLOR
    template.layout.polar.angularaxis.gridcolor = GRID_COLOR
    template.layout.polar.angularaxis.linecolor = AXIS_COLOR
    template.layout.polar.radialaxis.gridcolor = GRID_COLOR
    template.layout.polar.radialaxis.linecolor = AXIS_COLOR
    template.layout.ternary.bgcolor = BG_COLOR
    template.layout.ternary.aaxis.gridcolor = GRID_COLOR
    template.layout.ternary.aaxis.linecolor = AXIS_COLOR
    template.layout.ternary.baxis.gridcolor = GRID_COLOR
    template.layout.ternary.baxis.linecolor = AXIS_COLOR
    template.layout.ternary.caxis.gridcolor = GRID_COLOR
    template.layout.ternary.caxis.linecolor = AXIS_COLOR
    template.layout.mapbox.style = "carto-darkmatter"
    template.layout.coloraxis.colorbar.tickcolor = AXIS_COLOR
    template.layout.coloraxis.colorbar.tickfont.color = FONT_COLOR_SECONDARY
    template.layout.coloraxis.colorbar.title.font.color = FONT_COLOR_SECONDARY
    template.layout.xaxis.title.font.color = FONT_COLOR_PRIMARY
    template.layout.xaxis.tickcolor = AXIS_COLOR
    template.layout.xaxis.tickfont.color = FONT_COLOR_SECONDARY
    template.layout.xaxis.linecolor = AXIS_COLOR
    template.layout.xaxis.gridcolor = GRID_COLOR
    template.layout.yaxis.title.font.color = FONT_COLOR_PRIMARY
    template.layout.yaxis.tickcolor = AXIS_COLOR
    template.layout.yaxis.tickfont.color = FONT_COLOR_SECONDARY
    template.layout.yaxis.linecolor = AXIS_COLOR
    template.layout.yaxis.gridcolor = GRID_COLOR
    template.layout.annotationdefaults.font.color = FONT_COLOR_PRIMARY

    # "map" only available in plotly>=5.24.0, will replace "mapbox" soon. Until then, we need to set both.
    # We need the if statement here in case the user is using an older version of plotly.
    if "map" in template["layout"]:
        template.layout.map.style = "carto-darkmatter"

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
    return template.to_plotly_json()


if __name__ == "__main__":
    extracted_dark, extracted_light = extract_bs_variables_from_css_file(VARIABLES, CSS_FILE)
    template_dark = generate_json_template(extracted_dark)
    template_light = generate_json_template(extracted_light)

    parser = argparse.ArgumentParser(description="Generate JSON chart templates.")
    parser.add_argument("--check", help="check chart templates are up to date", action="store_true")
    args = parser.parse_args()

    for generated_template, file_name in zip([template_dark, template_light], ["vizro_dark.json", "vizro_light.json"]):
        existing_template_path = Path(f"{THEMES_FOLDER}/{file_name}")
        existing_template = json.loads(existing_template_path.read_text())

        if args.check:
            if existing_template != generated_template:
                sys.exit(f"Chart template `{file_name}` is out of date. Run `hatch run templates` to update it.")
            print(f"Chart template `{file_name}` is up to date 🎉")  # noqa: T201
        else:
            existing_template_path.write_text(json.dumps(generated_template, indent=4, cls=PlotlyJSONEncoder))
