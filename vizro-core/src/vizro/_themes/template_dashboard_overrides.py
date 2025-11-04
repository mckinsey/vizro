"""Modifications to vizro_light and vizro_dark to make charts suitable for dashboard."""

import plotly.graph_objs as go

from vizro._themes import colors

dashboard_overrides = go.layout.Template()
dashboard_overrides.layout = go.Layout(
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
