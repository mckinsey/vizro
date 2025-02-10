"""Modifications to vizro_light and vizro_dark to make charts suitable for dashboard."""

import plotly.graph_objs as go

BG_TRANSPARENT = "rgba(0, 0, 0, 0)"

dashboard_overrides = go.layout.Template()
dashboard_overrides.layout = go.Layout(
    title_pad_l=0,
    title_pad_r=0,
    margin_l=24,
    margin_t=24,
    margin_b=16,
    paper_bgcolor=BG_TRANSPARENT,
    plot_bgcolor=BG_TRANSPARENT,
    geo_bgcolor=BG_TRANSPARENT,
    geo_lakecolor=BG_TRANSPARENT,
    geo_landcolor=BG_TRANSPARENT,
    polar_bgcolor=BG_TRANSPARENT,
    ternary_bgcolor=BG_TRANSPARENT,
)
