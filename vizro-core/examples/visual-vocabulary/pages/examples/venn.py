import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture
from vizro.themes._palettes import qualitative


@capture("graph")
def venn_diagram_2(
    data_frame=None,
    label_a=None,
    label_b=None,
    label_intersection=None,
) -> go.Figure:
    fig = go.Figure()

    def get_label(column_name, default_value):
        if column_name is None or data_frame is None or data_frame.empty or column_name not in data_frame.columns:
            return default_value
        x = data_frame[column_name].dropna()
        return str(x.iloc[0]) if len(x) else default_value

    display_a = get_label(label_a, "A")
    display_b = get_label(label_b, "B")
    display_intersection = get_label(label_intersection, f"{display_a} & {display_b}")

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
    fig.add_annotation(x=1.5, y=2, text=display_a, showarrow=False, font={"size": 16})
    fig.add_annotation(x=3.5, y=2, text=display_b, showarrow=False, font={"size": 16})
    fig.add_annotation(x=2.5, y=2, text=display_intersection, showarrow=False, font={"size": 16})

    # Hide axes and set layout
    fig.update_xaxes(showline=False, showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showline=False, showgrid=False, zeroline=False, visible=False)
    fig.update_layout(
        yaxis={"scaleanchor": "x", "scaleratio": 1},
    )
    return fig


fig = venn_diagram_2(
    data_frame=pd.DataFrame(
        {
            "label_a": ["Product A", "Product A", None],
            "label_b": ["Product B", None, "Product B"],
            "label_intersection": ["Both", "Both", "Both"],
        }
    ),
    label_a="label_a",
    label_b="label_b",
    label_intersection="label_intersection",
)
