"""Modifications to vizro_light and vizro_dark to make charts suitable for dashboard."""

import plotly.graph_objs as go

dashboard_overrides = go.layout.Template(
    layout={"title": {"pad_l": 0, "pad_r": 0}, "margin_l": 24, "margin_t": 24, "margin_b": 16}
)
