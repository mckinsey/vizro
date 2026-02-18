"""Generates Plotly JSON templates for the dark and light themes."""

import argparse
import json
import re
import sys
from pathlib import Path

import plotly.io as pio
from plotly import graph_objects as go
from plotly.utils import PlotlyJSONEncoder

import vizro
from vizro.themes import colors, palettes

VIZRO_SRC_PATH = Path(vizro.__file__).parent

THEMES_FOLDER = VIZRO_SRC_PATH / "themes"
CSS_PATH = VIZRO_SRC_PATH / "static" / "css" / "vizro-bootstrap.min.css"
VARIABLES = ["--bs-primary", "--bs-secondary", "--bs-tertiary-color", "--bs-border-color", "--bs-body-bg"]


def create_template_common() -> go.layout.Template:
    """Creates template with common values for dark and light theme.

    Returns: A plotly template object, see https://plotly.com/python/reference/layout/.
    """
    return go.layout.Template(
        layout=go.Layout(
            annotationdefaults_font_size=14,
            annotationdefaults_showarrow=False,
            bargroupgap=0.1,
            # coloraxis_autocolorscale = False as otherwise users cannot customize
            # via `color_continuous_scale`. See https://github.com/plotly/plotly.py/issues/5433
            coloraxis_autocolorscale=False,
            coloraxis_colorbar_outlinewidth=0,
            coloraxis_colorbar_showticklabels=True,
            coloraxis_colorbar_thickness=20,
            coloraxis_colorbar_tickfont_size=14,
            coloraxis_colorbar_ticklabelposition="outside",
            coloraxis_colorbar_ticklen=8,
            coloraxis_colorbar_ticks="outside",
            coloraxis_colorbar_tickwidth=1,
            coloraxis_colorbar_title_font_size=14,
            # Diverging, sequential and sequential_minus colorscale will only be applied
            # automatically if `coloraxis_autocolorscale=True`. Otherwise, they have no
            # effect, and the default for continuous color scales will be the color
            # sequence applied to ["colorscale"]["sequential"].
            colorscale_diverging=palettes.diverging,
            colorscale_sequential=palettes.sequential,
            colorscale_sequentialminus=palettes.sequential_minus,
            colorway=palettes.qualitative,
            font_family="Inter, sans-serif, Arial",
            font_size=14,
            legend_bgcolor=colors.transparent,
            legend_font_size=14,
            legend_orientation="h",
            legend_title_font_size=14,
            legend_y=-0.20,
            map_style="carto-darkmatter",
            margin_autoexpand=True,
            margin_b=64,
            margin_l=80,
            margin_pad=0,
            margin_r=24,
            margin_t=64,
            # Normally, we should use the primary and secondary color for activecolor and color.
            # However, our rgba values are not displayed correctly with a transparent bg color.
            # Hence, we use darkgrey and dimgrey for now, which seems to work fine.
            modebar_activecolor="darkgrey",
            modebar_bgcolor=colors.transparent,
            modebar_color="dimgrey",
            showlegend=True,
            title_font_size=20,
            title_pad_b=0,
            title_pad_l=24,
            title_pad_r=24,
            title_pad_t=24,
            title_x=0,
            title_xanchor="left",
            title_xref="container",
            title_y=1,
            title_yanchor="top",
            title_yref="container",
            uniformtext_minsize=12,
            uniformtext_mode="hide",
            xaxis_automargin=True,
            xaxis_layer="below traces",
            xaxis_linewidth=1,
            xaxis_showline=True,
            xaxis_showticklabels=True,
            xaxis_tickfont_size=14,
            xaxis_ticklabelposition="outside",
            xaxis_ticklen=8,
            xaxis_ticks="outside",
            xaxis_tickwidth=1,
            xaxis_title_font_size=16,
            xaxis_title_standoff=8,
            xaxis_visible=True,
            xaxis_zeroline=False,
            yaxis_automargin=True,
            yaxis_layer="below traces",
            yaxis_linewidth=1,
            yaxis_showline=False,
            yaxis_showticklabels=True,
            yaxis_tickfont_size=14,
            yaxis_ticklabelposition="outside",
            yaxis_ticklen=8,
            yaxis_ticks="outside",
            yaxis_tickwidth=1,
            yaxis_title_font_size=16,
            yaxis_title_standoff=8,
            yaxis_visible=True,
            yaxis_zeroline=False,
        ),
        data=go.layout.template.Data(
            # Unfortunately, this doesn't apply to px charts and there doesn't
            # seem to be a way to set that default in px.
            pie=[go.Pie(textposition="auto", hole=0.5)],
            # Note theme-specific parts of the waterfall template are also
            # defined in this script.
            waterfall=[
                go.Waterfall(
                    decreasing_marker_color=colors.dark_purple,
                    increasing_marker_color=colors.blue,
                    totals_marker_color=colors.gray,
                    textposition="outside",
                    connector_line_width=1,
                )
            ],
        ),
    )


def extract_last_two_occurrences(variable: str, css_content: str) -> tuple[str | None, str | None]:
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
        dark_value, light_value = extract_last_two_occurrences(variable, css_content)
        cleaned_variable = variable.replace("--", "").upper()
        if dark_value and light_value:
            extracted_dark[cleaned_variable] = dark_value
            extracted_light[cleaned_variable] = light_value

    return extracted_dark, extracted_light


def create_theme_overrides(extracted_values: dict[str, str]) -> go.layout.Template:
    """Creates theme-specific template overrides.

    These are the parts that differ between light and dark themes.
    """
    FONT_COLOR_PRIMARY = extracted_values["BS-PRIMARY"]
    BG_COLOR = extracted_values["BS-BODY-BG"]
    FONT_COLOR_SECONDARY = extracted_values["BS-SECONDARY"]
    GRID_COLOR = extracted_values["BS-BORDER-COLOR"]
    AXIS_COLOR = extracted_values["BS-TERTIARY-COLOR"]

    return go.layout.Template(
        layout=go.Layout(
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
        ),
        data=go.layout.template.Data(
            bar=[go.Bar(marker_line_color=BG_COLOR)],
            waterfall=[go.Waterfall(textfont_color=FONT_COLOR_PRIMARY, connector_line_color=AXIS_COLOR)],
            sankey=[go.Sankey(link=dict(color=AXIS_COLOR))],
        ),
    )


def generate_json_template(extracted_values: dict[str, str]) -> go.layout.Template:
    """Generates the Plotly JSON chart template by merging common and theme-specific parts."""
    common = create_template_common()
    theme_overrides = create_theme_overrides(extracted_values)
    # Merge common template with theme-specific overrides
    template = pio.templates.merge_templates(common, theme_overrides)
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
