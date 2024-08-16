"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_data_table
from vizro.models.types import capture

df = px.data.iris()

@capture("graph")
def my_graph(data_frame):
    fig = px.scatter(data_frame, x="sepal_width", y="sepal_length")
    print(fig.layout.margin.t)  # This is None
    print(fig.layout.template.layout.margin.t)  # This is 64 our default
    fig.update_layout(margin_t=0)
    print(fig.layout.margin.t) # This is 0 now
    return fig

page = vm.Page(
    title="Test",
    layout=vm.Layout(
        grid=[[0, 1, 2]],
    ),
    components=[
        # Graph
        vm.Graph(figure=my_graph(df)),
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
