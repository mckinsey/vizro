from plotly import graph_objects as go

dashboard_overrides = go.layout.Template(
    layout=go.Layout(
        margin_b=16,
        margin_l=24,
        margin_t=24,
        title_pad_l=0,
        title_pad_r=0,
    )
)
