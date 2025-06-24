import numpy as np

from vizro import Vizro
import vizro.models as vm
import vizro.plotly.express as px
from vizro.models.types import capture
from dash import dcc

iris = px.data.iris()


@capture("action")
def my_custom_export(n_clicks):
    if n_clicks:
        print("my custom export action triggered-now!")
        return dcc.send_data_frame(iris.to_csv, "mydf.csv")


@capture("action")
def my_custom_location(n_clicks):
    if n_clicks:
        print("my custom location change action triggered-now!")
        return "/test-page-2"


page_1 = vm.Page(
    title="Test page",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
                ),
                vm.Graph(
                    id="graph",
                    figure=px.bar(
                        iris,
                        x="sepal_length",
                        y="sepal_width",
                        color="species",
                        title="Container I - Bar",
                    ),
                ),
                vm.Button(
                    id="button_download",
                    text="Export data!",
                    actions=[
                        vm.Action(
                            function=my_custom_export(),
                            inputs=["button_download.n_clicks"],
                            outputs=["vizro_download.data"],
                        )
                    ],
                ),
                vm.Button(
                    id="button_location",
                    text="Go to page 2!",
                    actions=[
                        vm.Action(
                            function=my_custom_location(),
                            inputs=["button_location.n_clicks"],
                            outputs=["vizro_url.href"],
                        )
                    ],
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
        )
    ],
)

page_2 = vm.Page(
    title="Test page 2",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
        )
    ],
)

dashboard = vm.Dashboard(title="Test dashboard", pages=[page_1, page_2])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
