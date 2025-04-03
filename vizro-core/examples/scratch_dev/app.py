import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.iris()


page1 = vm.Page(
    title="Page with custom container",
    components=[
        vm.Container(
            title="Inline default styling",
            components=[
                vm.Graph(
                    id="graph1",
                    figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
                ),
            ],
            variant="filled",
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(value=["setosa"], title="Species", extra={"inline": True}),
                    # targets=["graph1"]
                ),
            ],
        ),
        vm.Container(
            id="container_1",
            title="Inline custom styling",
            components=[
                vm.Graph(
                    id="graph2",
                    figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
                ),
            ],
            variant="outlined",
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(id="checklist", title="Species", extra={"inline": True}),
                    # targets=["graph2"]
                ),
            ],
        ),
    ],
)

# page2 = vm.Page(
#     title="Controls above tabs",
#     components=[
#         vm.Container(
#             title="Container with tabs and controls",
#             controls=[
#                 vm.Filter(
#                     column="species",
#                     selector=vm.Checklist(title="Species", extra={"inline": True}),
#                     targets=["graph3", "graph4"]
#                 )
#             ],
#             components=[
#                 vm.Tabs(
#                     tabs=[
#                         vm.Container(
#                             title="Tab1",
#                             components=[
#                                 vm.Graph(
#                                     id="graph3",
#                                     figure=px.scatter(df, x="sepal_length", y="petal_width", color="species",
#                                                       custom_data=["species"]),
#                                 ),
#                             ]
#                         ),
#                         vm.Container(
#                             title="Tab2",
#                             components=[
#                                 vm.Graph(
#                                     id="graph4",
#                                     figure=px.scatter(df, x="sepal_length", y="petal_width", color="species",
#                                                       custom_data=["species"]),
#                                 ),
#                             ]
#                         )
#                     ]
#                 )
#             ]
#         )
#     ]
# )

dashboard = vm.Dashboard(pages=[page1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
