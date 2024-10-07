import pandas as pd
import plotly.graph_objects as go
import vizro
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

# Create the pastry data
pastry = {
    'Pastry': ['Scones', 'Bagels', 'Muffins', 'Cakes', 'Donuts', 'Cookies'],
    'Neva': [9, 7, 4, 0, 0, 0],
    'Nope': [7, 6, 3, 0, 0, 0],
    'No': [5, 4, 3, 0, 0, 0],
    'Maybe': [0, 0, 0, 4, 7, 9],
    'Possible': [0, 0, 0, 3, 5, 8],
    'Yes': [0, 0, 0, 4, 6, 8]
}
pastry_df = pd.DataFrame(pastry)

@capture("graph")
def diverging_bar(data_frame, title=None):
    fig = go.Figure()
    
    # Add traces for negative side
    for col in data_frame.columns[1:4]:
        fig.add_trace(go.Bar(
            x=-data_frame[col].values,
            y=data_frame['Pastry'],
            orientation='h',
            name=col,
            customdata=data_frame[col],
            hovertemplate="%{y}: %{customdata}",
            marker_color=['#285a8d', '#327ac2', '#287cd2'][list(data_frame.columns[1:4]).index(col)]
        ))
    
    # Add traces for positive side
    for col in data_frame.columns[4:]:
        fig.add_trace(go.Bar(
            x=data_frame[col],
            y=data_frame['Pastry'],
            orientation='h',
            name=col,
            hovertemplate="%{y}: %{x}",
            marker_color=['#66B2FF', '#3399FF', '#0080FF'][list(data_frame.columns[4:]).index(col)]
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        barmode='relative',
        height=500,
        width=800,
        yaxis_autorange='reversed',
        bargap=0.1,
        legend_title_text='Categories',
        legend_orientation='h',
        legend_y=1.1,
        legend_x=0,
        xaxis_title="Rating",
        yaxis_title="Pastry"
    )
    
    # Add a vertical line at x=0
    fig.add_shape(
        type="line",
        x0=0, y0=-0.5,
        x1=0, y1=5.5,
        line=dict(color="black", width=2)
    )
    
    return fig

page_0 = vm.Page(
    title="Diverging Bar Chart",
    components=[
        vm.Graph(
            figure=diverging_bar(data_frame=pastry_df, title="Pastry Preference"),
        ),
    ],
    # Apply a filter to the custom chart
    controls=[
        vm.Filter(column="Pastry", selector=vm.Dropdown(title="Pastry Types", multi=True)),
    ],
)

dashboard = vm.Dashboard(pages=[page_0])

Vizro().build(dashboard).run()