"""General themed plotly template."""

from plotly import graph_objects as go

from vizro._themes._colors import get_colors


def create_template_common() -> go.layout.Template:
    """Creates template with common values for dark and light theme.

    Returns: A plotly template object, see https://plotly.com/python/reference/layout/.
    """
    COLORS = get_colors()
    template_common = go.layout.Template()
    template_common.layout = go.Layout(
        annotationdefaults_font_size=14,
        annotationdefaults_showarrow=False,
        bargroupgap=0.1,
        coloraxis_autocolorscale=False,  # Set to False as otherwise users cannot customize via `color_continous_scale`
        coloraxis_colorbar_outlinewidth=0,
        coloraxis_colorbar_showticklabels=True,
        coloraxis_colorbar_thickness=20,
        coloraxis_colorbar_tickfont_size=14,
        coloraxis_colorbar_ticklabelposition="outside",
        coloraxis_colorbar_ticklen=8,
        coloraxis_colorbar_ticks="outside",
        coloraxis_colorbar_tickwidth=1,
        coloraxis_colorbar_title_font_size=14,
        # Diverging, sequential and sequentialminus colorscale will only be applied automatically if
        # `coloraxis_autocolorscale=True`. Otherwise, they have no effect, and the default for continuous color scales
        # will be the color sequence applied to ["colorscale"]["sequential"].
        colorscale_diverging=COLORS["DIVERGING_RED_CYAN"],
        colorscale_sequential=COLORS["SEQUENTIAL_CYAN"],
        colorscale_sequentialminus=COLORS["SEQUENTIAL_RED"][::-1],
        colorway=COLORS["DISCRETE_10"],
        font_family="Inter, sans-serif, Arial",
        font_size=14,
        legend_bgcolor=COLORS["TRANSPARENT"],
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
        modebar_bgcolor=COLORS["TRANSPARENT"],
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
    )
    return template_common
