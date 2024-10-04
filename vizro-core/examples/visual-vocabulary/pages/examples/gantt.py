import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
import plotly.graph_objects as go

tasks = pd.DataFrame([
    dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28'),
    dict(Task="Job B", Start='2009-03-05', Finish='2009-04-15'),
    dict(Task="Job C", Start='2009-02-20', Finish='2009-05-30')
])

@capture("graph")
def gantt(data_frame: pd.DataFrame, x_start: str, x_end: str, y: str) -> go.Figure:
    fig = px.timeline(data_frame, x_start, x_end, y)
    fig.update_yaxes(autorange="reversed")
    return fig

page = vm.Page(
    title="Gantt",
    components=[vm.Graph(px.gantt(tasks, x_start="Start", x_end="Finish", y="Task"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
