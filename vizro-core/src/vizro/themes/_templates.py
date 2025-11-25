"""Dashboard-specific template overrides."""

from plotly import graph_objects as go

from vizro.themes import colors


dashboard_overrides = go.layout.Template(
    layout=go.Layout(
        geo_bgcolor=colors.transparent,
        geo_lakecolor=colors.transparent,
        geo_landcolor=colors.transparent,
        margin_b=16,
        margin_l=24,
        margin_t=24,
        paper_bgcolor=colors.transparent,
        plot_bgcolor=colors.transparent,
        polar_bgcolor=colors.transparent,
        ternary_bgcolor=colors.transparent,
        title_pad_l=0,
        title_pad_r=0,
    )
)
