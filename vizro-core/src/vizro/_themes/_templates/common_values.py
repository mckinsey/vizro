"""General themed plotly template."""

from plotly import graph_objects as go


def create_template_common():
    """Create general themed plotly template.

    Returns
    -------
        A plotly template object containing the general theme
        with optional keys specified here:
        https://plotly.com/python/reference/layout/

    """
    primary_font = "Inter, sans-serif, Arial"

    template_common = go.layout.Template()

    template_common.layout = go.Layout(
        # LAYOUT
        font_family=primary_font,
        font_size=14,
        title_font_family=primary_font,
        title_font_size=20,
        title_xref="container",
        title_yref="container",
        title_x=0,
        title_y=1,
        title_xanchor="left",
        title_yanchor="top",
        title_pad_l=80,
        title_pad_r=0,
        title_pad_t=24,
        title_pad_b=0,
        showlegend=True,
        legend_font_family=primary_font,
        legend_font_size=14,
        legend_orientation="h",
        legend_y=-0.20,
        legend_title_font_family=primary_font,
        legend_title_font_size=14,
        legend_title_text="",
        legend_bgcolor="rgba(0,0,0,0)",
        margin_l=80,
        margin_r=12,
        margin_t=64,
        margin_b=64,
        margin_pad=0,
        margin_autoexpand=True,
        coloraxis_autocolorscale=False,  # Set to False as otherwise users cannot customize via `color_continous_scale`
        coloraxis_colorbar_outlinewidth=0,
        coloraxis_colorbar_thickness=20,
        coloraxis_colorbar_showticklabels=True,
        coloraxis_colorbar_ticks="outside",
        coloraxis_colorbar_tickwidth=1,
        coloraxis_colorbar_ticklen=8,
        coloraxis_colorbar_tickfont_family=primary_font,
        coloraxis_colorbar_tickfont_size=14,
        coloraxis_colorbar_ticklabelposition="outside",
        coloraxis_colorbar_title_font_family=primary_font,
        coloraxis_colorbar_title_font_size=14,
        bargroupgap=0.1,
        uniformtext_minsize=12,
        uniformtext_mode="hide",
        # X AXIS
        xaxis_visible=True,
        xaxis_title_font_family=primary_font,
        xaxis_title_font_size=16,
        xaxis_title_standoff=8,
        xaxis_ticklabelposition="outside",
        xaxis_ticks="outside",
        xaxis_ticklen=8,
        xaxis_tickwidth=1,
        xaxis_showticklabels=True,
        xaxis_automargin=True,
        xaxis_tickfont_family=primary_font,
        xaxis_tickfont_size=14,
        xaxis_showline=True,
        xaxis_layer="below traces",
        xaxis_linewidth=1,
        xaxis_zeroline=False,
        # Y AXIS
        yaxis_visible=True,
        yaxis_title_font_family=primary_font,
        yaxis_title_font_size=16,
        yaxis_title_standoff=8,
        yaxis_ticklabelposition="outside",
        yaxis_ticks="outside",
        yaxis_ticklen=8,
        yaxis_tickwidth=1,
        yaxis_showticklabels=True,
        yaxis_automargin=True,
        yaxis_tickfont_family=primary_font,
        yaxis_tickfont_size=14,
        yaxis_showline=False,
        yaxis_layer="below traces",
        yaxis_linewidth=1,
        yaxis_zeroline=False,
    )

    return template_common
