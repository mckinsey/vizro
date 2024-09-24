"""Dark themed plotly template."""

from plotly import graph_objects as go
from plotly.graph_objs.layout._template import Template

from vizro._themes._color_values import COLORS
from vizro._themes._templates.common_values import create_template_common


def create_template_dark() -> Template:
    """Create dark themed plotly template.

    Returns:
        A plotly template object containing the dark theme

    """
    template_dark = create_template_common()

    # LAYOUT
    template_dark["layout"]["font"]["color"] = COLORS["WHITE_85"]
    template_dark["layout"]["title"]["font"]["color"] = COLORS["WHITE_85"]
    template_dark["layout"]["legend"]["font"]["color"] = COLORS["WHITE_85"]
    template_dark["layout"]["legend"]["title"]["font"]["color"] = COLORS["WHITE_85"]
    template_dark["layout"]["paper_bgcolor"] = COLORS["DARK_BG03"]
    template_dark["layout"]["plot_bgcolor"] = COLORS["DARK_BG03"]
    template_dark["layout"]["geo"]["bgcolor"] = COLORS["DARK_BG03"]
    template_dark["layout"]["geo"]["lakecolor"] = COLORS["DARK_BG03"]
    template_dark["layout"]["geo"]["landcolor"] = COLORS["DARK_BG03"]
    template_dark["layout"]["polar"]["bgcolor"] = COLORS["DARK_BG03"]
    template_dark["layout"]["polar"]["angularaxis"]["gridcolor"] = COLORS["WHITE_12"]
    template_dark["layout"]["polar"]["angularaxis"]["linecolor"] = COLORS["WHITE_30"]
    template_dark["layout"]["polar"]["radialaxis"]["gridcolor"] = COLORS["WHITE_12"]
    template_dark["layout"]["polar"]["radialaxis"]["linecolor"] = COLORS["WHITE_30"]
    template_dark["layout"]["ternary"]["bgcolor"] = COLORS["DARK_BG03"]
    template_dark["layout"]["ternary"]["aaxis"]["gridcolor"] = COLORS["WHITE_12"]
    template_dark["layout"]["ternary"]["aaxis"]["linecolor"] = COLORS["WHITE_30"]
    template_dark["layout"]["ternary"]["baxis"]["gridcolor"] = COLORS["WHITE_12"]
    template_dark["layout"]["ternary"]["baxis"]["linecolor"] = COLORS["WHITE_30"]
    template_dark["layout"]["ternary"]["caxis"]["gridcolor"] = COLORS["WHITE_12"]
    template_dark["layout"]["ternary"]["caxis"]["linecolor"] = COLORS["WHITE_30"]
    if "map" in template_dark["layout"]:
        # "map" only available in plotly>=5.24.0, will replace "mapbox" soon. Until then, we need to set both.
        # We need the if statement here in case the user is using an older version of plotly.
        template_dark["layout"]["map"]["style"] = "carto-darkmatter"
    template_dark["layout"]["mapbox"]["style"] = "carto-darkmatter"
    template_dark["layout"]["coloraxis"]["colorbar"]["tickcolor"] = COLORS["WHITE_30"]
    template_dark["layout"]["coloraxis"]["colorbar"]["tickfont"]["color"] = COLORS["WHITE_55"]
    template_dark["layout"]["coloraxis"]["colorbar"]["title"]["font"]["color"] = COLORS["WHITE_55"]
    # Diverging, sequential and sequentialminus colorscale will only be applied automatically if
    # `coloraxis_autocolorscale=True`. Otherwise, they have no effect, and the default for continuous color scales
    # will be the color sequence applied to ["colorscale"]["sequential"].
    template_dark["layout"]["colorscale"]["diverging"] = COLORS["DIVERGING_RED_CYAN"]
    template_dark["layout"]["colorscale"]["sequential"] = COLORS["SEQUENTIAL_CYAN"]
    template_dark["layout"]["colorscale"]["sequentialminus"] = COLORS["SEQUENTIAL_RED"][::-1]
    template_dark["layout"]["colorway"] = COLORS["DISCRETE_10"]

    # X AXIS
    template_dark["layout"]["xaxis"]["title"]["font"]["color"] = COLORS["WHITE_85"]
    template_dark["layout"]["xaxis"]["tickcolor"] = COLORS["WHITE_30"]
    template_dark["layout"]["xaxis"]["tickfont"]["color"] = COLORS["WHITE_55"]
    template_dark["layout"]["xaxis"]["linecolor"] = COLORS["WHITE_30"]
    template_dark["layout"]["xaxis"]["gridcolor"] = COLORS["WHITE_12"]

    # Y AXIS
    template_dark["layout"]["yaxis"]["title"]["font"]["color"] = COLORS["WHITE_85"]
    template_dark["layout"]["yaxis"]["tickcolor"] = COLORS["WHITE_30"]
    template_dark["layout"]["yaxis"]["tickfont"]["color"] = COLORS["WHITE_55"]
    template_dark["layout"]["yaxis"]["linecolor"] = COLORS["WHITE_30"]
    template_dark["layout"]["yaxis"]["gridcolor"] = COLORS["WHITE_12"]

    # ANNOTATIONS
    template_dark["layout"]["annotationdefaults"] = {
        "font": {"color": COLORS["WHITE_85"], "size": 14},
        "showarrow": False,
    }

    # CHART TYPES
    template_dark.data.bar = [
        go.Bar(
            # This hides the border lines in a bar chart created from unaggregated data.
            marker={"line": {"color": template_dark["layout"]["paper_bgcolor"]}},
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
