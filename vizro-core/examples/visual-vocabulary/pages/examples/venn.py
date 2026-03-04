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
        if (
            column_name is None
            or data_frame is None
            or data_frame.empty
            or column_name not in data_frame.columns
        ):
            return default_value
        x = data_frame[column_name].dropna()
        return str(x.iloc[0]) if len(x) else default_value

    display_a = get_label(label_a, "A")
    display_b = get_label(label_b, "B")
    
    # intersection display - keep it simple, or combine
    val_intersection = get_label(label_intersection, None)
    if val_intersection is None:
        display_intersection = f"{display_a} & {display_b}"
    else:
        display_intersection = val_intersection

    # Add an invisible trace so Plotly correctly renders the custom Cartesian modebar configurations
    fig.add_trace(
        go.Scatter(
            x=[2.5],
            y=[2],
            mode="markers",
            marker_color="rgba(0,0,0,0)",
            showlegend=False,
            hoverinfo="skip",
        )
    )

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
    fig.add_annotation(x=1.35, y=2, text=display_a, showarrow=False, font={"size": 13})
    fig.add_annotation(x=3.65, y=2, text=display_b, showarrow=False, font={"size": 13})
    fig.add_annotation(
        x=2.5, y=2, text=display_intersection, showarrow=False, font={"size": 13}
    )

    # Hide axes and set layout
    fig.update_xaxes(showline=False, showgrid=False, zeroline=False, visible=False, fixedrange=True, range=[0.75, 4.25])
    fig.update_yaxes(showline=False, showgrid=False, zeroline=False, visible=False, fixedrange=True, range=[0.75, 3.25])
    fig.update_layout(
        margin={"l": 20, "r": 20, "b": 20},
        showlegend=False,
        yaxis={"scaleanchor": "x", "scaleratio": 1},
        modebar_remove=[
            "zoom",
            "pan",
            "select",
            "lasso",
            "zoomIn",
            "zoomOut",
            "autoScale",
            "resetScale",
            "zoom2d",
            "pan2d",
            "select2d",
            "lasso2d",
            "zoomIn2d",
            "zoomOut2d",
            "autoScale2d",
            "resetScale2d",
        ],
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
