import pandas as pd
import vizro.plotly.express as px

tasks = pd.DataFrame(
    [
        {"Task": "Job A", "Start": "2009-01-01", "Finish": "2009-02-28"},
        {"Task": "Job B", "Start": "2009-03-05", "Finish": "2009-04-15"},
        {"Task": "Job C", "Start": "2009-02-20", "Finish": "2009-05-30"},
    ]
).sort_values("Start", ascending=False)

fig = px.timeline(tasks, x_start="Start", x_end="Finish", y="Task")
