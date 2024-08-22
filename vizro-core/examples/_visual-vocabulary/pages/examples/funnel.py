import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

funnel_data = pd.DataFrame(
    {"Stage": ["Leads", "Sales calls", "Follow-up", "Conversion", "Sales"], "Value": [10, 7, 4, 2, 1]}
)

page = vm.Page(
    title="Funnel",
    components=[vm.Graph(figure=px.funnel_area(funnel_data, names="Stage", values="Value"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
