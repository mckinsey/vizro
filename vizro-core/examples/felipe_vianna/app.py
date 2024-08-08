import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
import plotly.graph_objects as go


@capture("graph")
def scatter_with_line(data_frame, x, y, hline=None, **kwargs):
    scatter_fig = px.scatter(data_frame=data_frame, x=x, y=y, **kwargs)

    # Add hline to the scatter_fig
    scatter_fig.add_hline(y=hline, line_color="gray")

    # average value of selected 'y' per species
    avg_y = data_frame.groupby('species')[y].mean().reset_index()
    average_dots = go.Scatter(
        x=[data_frame[x].min()] * len(avg_y),
        y=avg_y[y],
        mode='markers',
        marker=dict(size=30, symbol='bowtie'),
        text=avg_y['species'],
        name=f'Average {y} per species',
        marker_color=["#00b4ff", "#ff9222", "#3949ab"]
    )

    # add go.Scatter to the scatter_fig
    scatter_fig.add_trace(average_dots)

    return scatter_fig


page_0 = vm.Page(
    title="Custom chart",
    components=[
        vm.Graph(
            id="enhanced_scatter",
            figure=scatter_with_line(
                data_frame=px.data.iris(),
                x="sepal_length",
                y="sepal_width",
                color="species",
                size="petal_width",
                hline=3,
            ),
        ),
    ],
    controls=[
        vm.Filter(column="species"),
        vm.Parameter(
            targets=["enhanced_scatter.hline"],
            selector=vm.Slider(min=2, max=5, step=1, value=3, title="Horizontal line"),
        ),
        vm.Parameter(
            targets=["enhanced_scatter.y"],
            selector=vm.Dropdown(
                title="Choose Y-axis",
                options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                multi=False,
                value="sepal_width",
            ),
        ),
    ],
)
dashboard = vm.Dashboard(pages=[page_0])

Vizro().build(dashboard).run()
