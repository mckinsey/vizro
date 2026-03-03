import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture
from vizro.themes._palettes import qualitative


@capture("graph")
def venn_diagram_2(data_frame=None, label_a="A", label_b="B", label_intersection=None) -> go.Figure:
    label_intersection = label_intersection or f"{label_a} & {label_b}"

    fig = go.Figure()

    # Add circles
    fig.add_shape(
        type="circle",
        line_color=qualitative[0],
        fillcolor=qualitative[0],
        x0=1,
        y0=1,
        x1=3,
        y1=3,
        opacity=0.3,
    )
    fig.add_shape(
        type="circle",
        line_color=qualitative[1],
        fillcolor=qualitative[1],
        x0=2,
        y0=1,
        x1=4,
        y1=3,
        opacity=0.3,
    )

    # Add annotations
    fig.add_annotation(x=1.5, y=2, text=label_a, showarrow=False, font={"size": 16})
    fig.add_annotation(x=3.5, y=2, text=label_b, showarrow=False, font={"size": 16})
    fig.add_annotation(x=2.5, y=2, text=label_intersection, showarrow=False, font={"size": 16})

    # Hide axes and set layout
    fig.update_xaxes(showline=False, showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showline=False, showgrid=False, zeroline=False, visible=False)
    fig.update_layout(margin={"l": 20, "r": 20, "b": 20}, showlegend=False)
    return fig


fig = venn_diagram_2(data_frame=pd.DataFrame())
