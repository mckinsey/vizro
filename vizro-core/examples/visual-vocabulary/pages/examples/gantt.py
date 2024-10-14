import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tasks = pd.DataFrame(
    [
        {"Task": "Job A", "Start": "2009-01-01", "Finish": "2009-02-28"},
        {"Task": "Job B", "Start": "2009-03-05", "Finish": "2009-04-15"},
        {"Task": "Job C", "Start": "2009-02-20", "Finish": "2009-05-30"},
    ]
)


page = vm.Page(
    title="Gantt",
    components=[
        vm.Graph(px.timeline(tasks.sort_values("Start", ascending=False), x_start="Start", x_end="Finish", y="Task"))
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
