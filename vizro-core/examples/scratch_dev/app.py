import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()

page = vm.Page(
    title="Containers with controls",
    components=[
        vm.Container(
            title="Container with gapminder data",
            components=[vm.Graph(id="bar_chart", figure=px.bar(gapminder, x="country", y="gdpPercap"))],
            controls=[
                vm.Filter(column="continent", selector=vm.RadioItems()),
                vm.Filter(column="year", selector=vm.RangeSlider(title="This is a longer title and it goes and goes")),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
