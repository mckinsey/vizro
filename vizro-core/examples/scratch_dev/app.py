"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_data_table

df = px.data.iris()


page = vm.Page(
    title="Test",
    layout=vm.Layout(
        grid=[[0, 1, 2]],
    ),
    components=[
        # Graph
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", title="My Graph")),
        vm.Table(figure=dash_data_table(df), title="My Table"),
        vm.Graph(
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", title="My Graph <br><span>This is a subtitle</span>"
            )
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
