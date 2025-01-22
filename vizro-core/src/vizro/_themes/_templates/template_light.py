"""Light themed plotly template."""

from plotly import graph_objects as go
from plotly.graph_objs.layout._template import Template

from vizro._themes._color_values import COLORS
from vizro._themes._templates.common_values import create_template_common

# VARIABLES
FONT_COLOR_PRIMARY = COLORS["BLACK_85"]
FONT_COLOR_SECONDARY = COLORS["BLACK_55"]
BG_COLOR = COLORS["Light_BG01"]
GRID_COLOR = COLORS["BLACK_12"]
AXIS_COLOR = COLORS["BLACK_30"]


def create_template_light() -> Template:
    """Create light themed plotly template.

    Returns:
    -------
        A plotly template object containing the light theme

    """
    template_light = create_template_common()

    # LAYOUT
    template_light["layout"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_light["layout"]["title"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_light["layout"]["legend"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_light["layout"]["legend"]["title"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_light["layout"]["paper_bgcolor"] = BG_COLOR
    template_light["layout"]["plot_bgcolor"] = BG_COLOR
    template_light["layout"]["geo"]["bgcolor"] = BG_COLOR
    template_light["layout"]["geo"]["lakecolor"] = BG_COLOR
    template_light["layout"]["geo"]["landcolor"] = BG_COLOR
    template_light["layout"]["polar"]["bgcolor"] = BG_COLOR
    template_light["layout"]["polar"]["angularaxis"]["gridcolor"] = GRID_COLOR
    template_light["layout"]["polar"]["angularaxis"]["linecolor"] = AXIS_COLOR
    template_light["layout"]["polar"]["radialaxis"]["gridcolor"] = GRID_COLOR
    template_light["layout"]["polar"]["radialaxis"]["linecolor"] = AXIS_COLOR
    template_light["layout"]["ternary"]["bgcolor"] = BG_COLOR
    template_light["layout"]["ternary"]["aaxis"]["gridcolor"] = GRID_COLOR
    template_light["layout"]["ternary"]["aaxis"]["linecolor"] = AXIS_COLOR
    template_light["layout"]["ternary"]["baxis"]["gridcolor"] = GRID_COLOR
    template_light["layout"]["ternary"]["baxis"]["linecolor"] = AXIS_COLOR
    template_light["layout"]["ternary"]["caxis"]["gridcolor"] = GRID_COLOR
    template_light["layout"]["ternary"]["caxis"]["linecolor"] = AXIS_COLOR
    if "map" in template_light["layout"]:
        # "map" only available in plotly>=5.24.0, will replace "mapbox" soon. Until then, we need to set both.
        # We need the if statement here in case the user is using an older version of plotly.
        template_light["layout"]["map"]["style"] = "carto-positron"
    template_light["layout"]["mapbox"]["style"] = "carto-positron"
    template_light["layout"]["coloraxis"]["colorbar"]["tickcolor"] = AXIS_COLOR
    template_light["layout"]["coloraxis"]["colorbar"]["tickfont"]["color"] = FONT_COLOR_SECONDARY
    template_light["layout"]["coloraxis"]["colorbar"]["title"]["font"]["color"] = FONT_COLOR_SECONDARY

    # X AXIS
    template_light["layout"]["xaxis"]["title"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_light["layout"]["xaxis"]["tickcolor"] = AXIS_COLOR
    template_light["layout"]["xaxis"]["tickfont"]["color"] = FONT_COLOR_SECONDARY
    template_light["layout"]["xaxis"]["linecolor"] = AXIS_COLOR
    template_light["layout"]["xaxis"]["gridcolor"] = GRID_COLOR

    # Y AXIS
    template_light["layout"]["yaxis"]["title"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_light["layout"]["yaxis"]["tickcolor"] = AXIS_COLOR
    template_light["layout"]["yaxis"]["tickfont"]["color"] = FONT_COLOR_SECONDARY
    template_light["layout"]["yaxis"]["linecolor"] = AXIS_COLOR
    template_light["layout"]["yaxis"]["gridcolor"] = GRID_COLOR

    # ANNOTATIONS
    template_light["layout"]["annotationdefaults"] = {
        "font": {"color": FONT_COLOR_PRIMARY, "size": 14},
        "showarrow": False,
    }

    # CHART TYPES
    template_light.data.bar = [
        go.Bar(
            # This hides the border lines in a bar chart created from unaggregated data.
            marker={"line": {"color": template_light.layout.paper_bgcolor}},
        )
    ]

    template_light.data.waterfall = [
        go.Waterfall(
            decreasing={"marker": {"color": COLORS["DISCRETE_10"][1]}},
            increasing={"marker": {"color": COLORS["DISCRETE_10"][0]}},
            totals={"marker": {"color": COLORS["GREY_30"]}},
            textfont_color=template_light.layout.title.font.color,
            textposition="outside",
            connector={"line": {"color": template_light.layout.xaxis.tickcolor, "width": 1}},
        )
    ]

    return template_light


light = create_template_light()
