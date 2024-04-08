"""Light themed plotly template."""

from plotly import graph_objects as go
from plotly.graph_objs.layout._template import Template

from vizro._themes._color_values import COLORS
from vizro._themes._templates.common_values import create_template_common


def create_template_light() -> Template:
    """Create light themed plotly template.

    Returns
    -------
        A plotly template object containing the light theme

    """
    template_light = create_template_common()

    # LAYOUT
    template_light["layout"]["font"]["color"] = COLORS["BLACK_85"]
    template_light["layout"]["title"]["font"]["color"] = COLORS["BLACK_85"]
    template_light["layout"]["legend"]["font"]["color"] = COLORS["BLACK_85"]
    template_light["layout"]["legend"]["title"]["font"]["color"] = COLORS["BLACK_85"]
    template_light["layout"]["paper_bgcolor"] = COLORS["Light_BG01"]
    template_light["layout"]["plot_bgcolor"] = COLORS["Light_BG01"]
    template_light["layout"]["geo"]["bgcolor"] = COLORS["Light_BG01"]
    template_light["layout"]["geo"]["lakecolor"] = COLORS["Light_BG01"]
    template_light["layout"]["geo"]["landcolor"] = COLORS["Light_BG01"]
    template_light["layout"]["polar"]["bgcolor"] = COLORS["Light_BG01"]
    template_light["layout"]["polar"]["angularaxis"]["gridcolor"] = COLORS["BLACK_12"]
    template_light["layout"]["polar"]["angularaxis"]["linecolor"] = COLORS["BLACK_30"]
    template_light["layout"]["polar"]["radialaxis"]["gridcolor"] = COLORS["BLACK_12"]
    template_light["layout"]["polar"]["radialaxis"]["linecolor"] = COLORS["BLACK_30"]
    template_light["layout"]["ternary"]["bgcolor"] = COLORS["Light_BG01"]
    template_light["layout"]["ternary"]["aaxis"]["gridcolor"] = COLORS["BLACK_12"]
    template_light["layout"]["ternary"]["aaxis"]["linecolor"] = COLORS["BLACK_30"]
    template_light["layout"]["ternary"]["baxis"]["gridcolor"] = COLORS["BLACK_12"]
    template_light["layout"]["ternary"]["baxis"]["linecolor"] = COLORS["BLACK_30"]
    template_light["layout"]["ternary"]["caxis"]["gridcolor"] = COLORS["BLACK_12"]
    template_light["layout"]["ternary"]["caxis"]["linecolor"] = COLORS["BLACK_30"]
    template_light["layout"]["mapbox"]["style"] = "carto-positron"
    template_light["layout"]["coloraxis"]["colorbar"]["tickcolor"] = COLORS["BLACK_30"]
    template_light["layout"]["coloraxis"]["colorbar"]["tickfont"]["color"] = COLORS["BLACK_55"]
    template_light["layout"]["coloraxis"]["colorbar"]["title"]["font"]["color"] = COLORS["BLACK_55"]
    template_light["layout"]["colorscale"]["diverging"] = COLORS["DIVERGING_RED_CYAN"]
    template_light["layout"]["colorscale"]["sequential"] = COLORS["SEQUENTIAL_CYAN"]
    template_light["layout"]["colorscale"]["sequentialminus"] = COLORS["SEQUENTIAL_RED"][::-1]
    template_light["layout"]["colorway"] = COLORS["DISCRETE_10"]

    # X AXIS
    template_light["layout"]["xaxis"]["title"]["font"]["color"] = COLORS["BLACK_85"]
    template_light["layout"]["xaxis"]["tickcolor"] = COLORS["BLACK_30"]
    template_light["layout"]["xaxis"]["tickfont"]["color"] = COLORS["BLACK_55"]
    template_light["layout"]["xaxis"]["linecolor"] = COLORS["BLACK_30"]
    template_light["layout"]["xaxis"]["gridcolor"] = COLORS["BLACK_12"]

    # Y AXIS
    template_light["layout"]["yaxis"]["title"]["font"]["color"] = COLORS["BLACK_85"]
    template_light["layout"]["yaxis"]["tickcolor"] = COLORS["BLACK_30"]
    template_light["layout"]["yaxis"]["tickfont"]["color"] = COLORS["BLACK_55"]
    template_light["layout"]["yaxis"]["linecolor"] = COLORS["BLACK_30"]
    template_light["layout"]["yaxis"]["gridcolor"] = COLORS["BLACK_12"]

    # ANNOTATIONS
    template_light["layout"]["annotationdefaults"] = {
        "font": {"color": COLORS["BLACK_85"], "size": 14},
        "showarrow": False,
    }

    # CHART TYPES
    template_light.data.bar = [
        go.Bar(marker={"line": {"color": template_light["layout"]["paper_bgcolor"], "width": 1}})
    ]

    template_light.data.table = [
        go.Table(
            header={
                "fill_color": COLORS["Light_BG01"],
                "line_color": COLORS["BLACK_12"],
                "height": 32,
                "font": {"color": COLORS["BLACK_85"], "size": 14},
                "align": "left",
            },
            cells={
                "line_color": COLORS["BLACK_12"],
                "fill_color": COLORS["Light_BG01"],
                "height": 32,
                "font": {"color": COLORS["BLACK_55"], "size": 14},
                "align": "left",
            },
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
