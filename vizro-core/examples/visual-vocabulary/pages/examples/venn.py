import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def venn_diagram(data_frame=None, **kwargs) -> go.Figure:
    fig = go.Figure()

    # Add circles
    fig.add_shape(
        type="circle",
        line_color="blue",
        fillcolor="blue",
        x0=1,
        y0=1,
        x1=3,
        y1=3,
        opacity=0.3,
    )
    fig.add_shape(
        type="circle",
        line_color="gray",
        fillcolor="gray",
        x0=2,
        y0=1,
        x1=4,
        y1=3,
        opacity=0.3,
    )

    # Add annotations
    fig.add_annotation(x=1.5, y=2, text="Group A", showarrow=False, font={"size": 16})
    fig.add_annotation(x=3.5, y=2, text="Group B", showarrow=False, font={"size": 16})
    fig.add_annotation(x=2.5, y=2, text="A & B", showarrow=False, font={"size": 16})

    # Hide axes and set layout
    fig.update_xaxes(showline=False, showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showline=False, showgrid=False, zeroline=False, visible=False)
    fig.update_layout(margin={"l": 20, "r": 20, "b": 20}, showlegend=False)
    return fig


fig = venn_diagram(data_frame=pd.DataFrame())
