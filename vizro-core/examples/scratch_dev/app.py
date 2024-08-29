"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_data_table

df = px.data.iris()


page = vm.Page(
    title="Testasfsadfsadf",
    layout=vm.Layout(
        grid=[[0, 1, 2, 3]],
    ),
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length")),
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", title="Blah blah")),
        vm.Table(figure=dash_data_table(df), title="My Table"),
        vm.Container(
            id="container-with-different-bg",
            title="Container Title",
            components=[
                vm.Graph(
                    figure=px.scatter(
                        df, x="sepal_width", y="sepal_length", title="My Graph <br><span>This is a subtitle</span>"
                    )
                )
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
