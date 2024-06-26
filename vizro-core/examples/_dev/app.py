"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture
from vizro.actions import filter_interaction

df = px.data.iris()


@capture("graph")
def my_graph(data_frame, custom_data=None):
    return px.scatter(
        data_frame,
        title="Title",
        x="sepal_width",
        y="sepal_length",
        color="species",
        # This does not work
        custom_data=["species"],
        # This works
        # custom_data=custom_data
    )


page = vm.Page(
    title="",
    components=[
        vm.Graph(
            id="graph_1",
            figure=my_graph(
                data_frame=df,
                # custom_data has to be propagated to the custom graph function to make the filter_interaction to work.
                # custom_data=["species"],
            ),
            actions=[
                vm.Action(function=filter_interaction(targets=["graph_2"]))
            ],
        ),
        vm.Graph(
            id="graph_2",
            figure=px.scatter(df, title="Title", x="sepal_width", y="sepal_length", color="species")
        ),
    ],
    controls=[
        vm.Filter(column="species")
    ]
)



dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
