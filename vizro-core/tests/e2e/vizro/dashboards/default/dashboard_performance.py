import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df_list = [px.data.iris()]
for i in range(1, 33333):
    df_list.append(px.data.iris())  # noqa PERF401
iris = pd.concat(df_list)


page_with_chart_filter_parameter = vm.Page(
    title="Page with chart, filter and parameter",
    components=[
        vm.Graph(
            id="histogram_chart",
            figure=px.histogram(
                iris,
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown()),
        vm.Parameter(
            targets=["histogram_chart.y"],
            selector=vm.RadioItems(options=["petal_width", "petal_length"], value="petal_width"),
        ),
    ],
)


dashboard = vm.Dashboard(pages=[page_with_chart_filter_parameter])

app = Vizro().build(dashboard)
app.dash.enable_dev_tools(debug=True, dev_tools_ui=True, dev_tools_hot_reload=False)

if __name__ == "__main__":
    app.run()
