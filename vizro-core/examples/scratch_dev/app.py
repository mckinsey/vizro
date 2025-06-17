import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

page = vm.Page(
    title="Containers with controls",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab with iris data",
                    components=[vm.Graph(figure=px.bar(iris, x="species", y="sepal_length"))],
                    controls=[
                        vm.Filter(column="petal_length", selector=vm.Slider()),
                        vm.Filter(column="sepal_length", selector=vm.RangeSlider()),
                    ],
                ),
            ]
        ),
        vm.Container(
            title="Container with iris data",
            components=[vm.Graph(figure=px.bar(iris, x="species", y="sepal_length"))],
            controls=[
                vm.Filter(column="petal_length", selector=vm.Slider()),
                vm.Filter(column="sepal_length", selector=vm.RangeSlider()),
            ],
        ),
    ],
    controls=[vm.Filter(column="sepal_length", selector=vm.RangeSlider())],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
