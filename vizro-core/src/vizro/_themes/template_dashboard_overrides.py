"""Modifications to vizro_light and vizro_dark to make charts suitable for dashboard."""

import plotly.graph_objs as go

TRANSPARENT = "rgba(0, 0, 0, 0)"

dashboard_overrides = go.layout.Template()
dashboard_overrides.layout = go.Layout(
    geo_bgcolor=TRANSPARENT,
    geo_lakecolor=TRANSPARENT,
    geo_landcolor=TRANSPARENT,
    margin_b=16,
    margin_l=24,
    margin_t=24,
    paper_bgcolor=TRANSPARENT,
    plot_bgcolor=TRANSPARENT,
    polar_bgcolor=TRANSPARENT,
    ternary_bgcolor=TRANSPARENT,
    title_pad_l=0,
    title_pad_r=0,
)
