"""Dark themed plotly template."""

from plotly import graph_objects as go
from plotly.graph_objs.layout._template import Template

from vizro._themes._color_values import COLORS
from vizro._themes._templates.common_values import create_template_common

# VARIABLES
FONT_COLOR_PRIMARY = COLORS["WHITE_85"]
FONT_COLOR_SECONDARY = COLORS["WHITE_55"]
BG_COLOR = COLORS["DARK_BG03"]
GRID_COLOR = COLORS["WHITE_12"]
AXIS_COLOR = COLORS["WHITE_30"]


def create_template_dark() -> Template:
    """Create dark themed plotly template.

    Returns:
        A plotly template object containing the dark theme

    """
    template_dark = create_template_common()

    # LAYOUT
    template_dark["layout"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_dark["layout"]["title"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_dark["layout"]["legend"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_dark["layout"]["legend"]["title"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_dark["layout"]["paper_bgcolor"] = BG_COLOR
    template_dark["layout"]["plot_bgcolor"] = BG_COLOR
    template_dark["layout"]["geo"]["bgcolor"] = BG_COLOR
    template_dark["layout"]["geo"]["lakecolor"] = BG_COLOR
    template_dark["layout"]["geo"]["landcolor"] = BG_COLOR
    template_dark["layout"]["polar"]["bgcolor"] = BG_COLOR
    template_dark["layout"]["polar"]["angularaxis"]["gridcolor"] = GRID_COLOR
    template_dark["layout"]["polar"]["angularaxis"]["linecolor"] = AXIS_COLOR
    template_dark["layout"]["polar"]["radialaxis"]["gridcolor"] = GRID_COLOR
    template_dark["layout"]["polar"]["radialaxis"]["linecolor"] = AXIS_COLOR
    template_dark["layout"]["ternary"]["bgcolor"] = BG_COLOR
    template_dark["layout"]["ternary"]["aaxis"]["gridcolor"] = GRID_COLOR
    template_dark["layout"]["ternary"]["aaxis"]["linecolor"] = AXIS_COLOR
    template_dark["layout"]["ternary"]["baxis"]["gridcolor"] = GRID_COLOR
    template_dark["layout"]["ternary"]["baxis"]["linecolor"] = AXIS_COLOR
    template_dark["layout"]["ternary"]["caxis"]["gridcolor"] = GRID_COLOR
    template_dark["layout"]["ternary"]["caxis"]["linecolor"] = AXIS_COLOR
    if "map" in template_dark["layout"]:
        # "map" only available in plotly>=5.24.0, will replace "mapbox" soon. Until then, we need to set both.
        # We need the if statement here in case the user is using an older version of plotly.
        template_dark["layout"]["map"]["style"] = "carto-darkmatter"
    template_dark["layout"]["mapbox"]["style"] = "carto-darkmatter"
    template_dark["layout"]["coloraxis"]["colorbar"]["tickcolor"] = AXIS_COLOR
    template_dark["layout"]["coloraxis"]["colorbar"]["tickfont"]["color"] = FONT_COLOR_SECONDARY
    template_dark["layout"]["coloraxis"]["colorbar"]["title"]["font"]["color"] = FONT_COLOR_SECONDARY

    # X AXIS
    template_dark["layout"]["xaxis"]["title"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_dark["layout"]["xaxis"]["tickcolor"] = AXIS_COLOR
    template_dark["layout"]["xaxis"]["tickfont"]["color"] = FONT_COLOR_SECONDARY
    template_dark["layout"]["xaxis"]["linecolor"] = AXIS_COLOR
    template_dark["layout"]["xaxis"]["gridcolor"] = GRID_COLOR

    # Y AXIS
    template_dark["layout"]["yaxis"]["title"]["font"]["color"] = FONT_COLOR_PRIMARY
    template_dark["layout"]["yaxis"]["tickcolor"] = AXIS_COLOR
    template_dark["layout"]["yaxis"]["tickfont"]["color"] = FONT_COLOR_SECONDARY
    template_dark["layout"]["yaxis"]["linecolor"] = AXIS_COLOR
    template_dark["layout"]["yaxis"]["gridcolor"] = GRID_COLOR

    # ANNOTATIONS
    template_dark["layout"]["annotationdefaults"] = {
        "font": {"color": FONT_COLOR_PRIMARY, "size": 14},
        "showarrow": False,
    }

    # CHART TYPES
    template_dark.data.bar = [
        go.Bar(
            # This hides the border lines in a bar chart created from unaggregated data.
            marker={"line": {"color": template_dark.layout.paper_bgcolor}},
        )
    ]

    template_dark.data.waterfall = [
        go.Waterfall(
            decreasing={"marker": {"color": COLORS["DISCRETE_10"][1]}},
            increasing={"marker": {"color": COLORS["DISCRETE_10"][0]}},
            totals={"marker": {"color": COLORS["GREY_55"]}},
            textfont_color=template_dark.layout.title.font.color,
            textposition="outside",
            connector={"line": {"color": template_dark.layout.xaxis.tickcolor, "width": 1}},
        )
    ]
    return template_dark


dark = create_template_dark()
