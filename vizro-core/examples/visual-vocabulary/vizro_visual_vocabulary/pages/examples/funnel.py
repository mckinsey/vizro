import pandas as pd
import vizro.plotly.express as px

funnel_data = pd.DataFrame(
    {"Stage": ["Leads", "Sales calls", "Follow-up", "Conversion", "Sales"], "Value": [10, 7, 4, 2, 1]}
)

fig = px.funnel_area(funnel_data, names="Stage", values="Value")
