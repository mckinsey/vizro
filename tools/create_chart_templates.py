import re
import json
from plotly.utils import PlotlyJSONEncoder
from vizro._themes.common_values import create_template_common
from vizro._themes._color_values import COLORS
from plotly import graph_objects as go
import pathlib
# File paths
CSS_FILE = "../vizro-core/src/vizro/static/css/vizro-bootstrap.min.css"
OUTPUT_FILE = "../vizro-core/src/vizro/_themes/vizro_dark.json"

# List of CSS variables to extract
VARIABLES = [
    '--bs-primary',
    '--bs-secondary',
    '--bs-tertiary-color',
    '--bs-border-color',
    '--bs-body-bg'
]

def _extract_last_two_occurrences(variable, content):
    """Extract the last two occurrences of a variable from the CSS content."""
    pattern = re.compile(rf'{variable}:\s*([^;]+);')
    matches = pattern.findall(content)
    if len(matches) >= 2:
        return matches[-2].strip(), matches[-1].strip()
    return None, None


def extract_bs_variables_from_css_file(variables, css_file_path):
    """Extract the last two occurrences for each variable in the list."""
    extracted_values = {}

    with open(css_file_path, 'r') as css_content:
        for variable in variables:
            dark_values, light_values = _extract_last_two_occurrences(variable, css_content.read())
            extracted_values[f'{variable[2:].upper()}'] = dark_values
           # extracted_values["LIGHT"][f'{variable[2:].upper()}'] = light_values
    return extracted_values


def generate_json_templates(extracted_values):
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
    if "map" in template.layout:
        template.layout.map.style = "carto-darkmatter"

    template.data.bar = [go.Bar(marker_line_color= BG_COLOR)]
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


def write_json_file(file_path, template):
    """Write the generated content to the specified Python file."""
    #with open(file_path, "w") as file:
    #    json.dump(template, file,  indent=4, cls=PlotlyJSONEncoder)
    pathlib.Path(file_path).write_text(json.dumps(template, indent=4, cls=PlotlyJSONEncoder))


if __name__ == "__main__":
    extracted_values = extract_bs_variables_from_css_file(VARIABLES, CSS_FILE)
    chart_template = generate_json_templates(extracted_values)
    write_json_file(OUTPUT_FILE, chart_template)
    print("🎉 The templates have been successfully created!")
