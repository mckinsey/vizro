"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data

df = px.data.iris()


page = vm.Page(
    title="Page 1",
    components=[
        vm.Graph(figure=px.bar(df, x="sepal_width", y="sepal_length")),
        vm.Button(
            text="Export data",
            actions=[
                vm.Action(function=export_data()),
                vm.Action(function=export_data()),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
    # print(dashboard._to_python())
    # print(dashboard.model_dump(context={"add_name": True}))
