from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm

gapminder_2007 = px.data.gapminder().query("year == 2007")

page_1 = vm.Page(
    title="Page with button",
    layout=vm.Grid(grid=[[0, 1, 2, 3, 4], [5, 5, 5, 5, 5], [5, 5, 5, 5, 5]]),
    components=[
        vm.Container(
            title="Plain button",
            components=[
                vm.Button(text="Click me!", description=vm.Tooltip(text="Button tooltip", icon="info"), variant="plain")
            ],
            variant="outlined",
        ),
        vm.Container(
            title="Filled button",
            components=[vm.Button(text="Click me!", description=vm.Tooltip(text="Button tooltip", icon="info"))],
            variant="outlined",
        ),
        vm.Container(
            title="Outlined button",
            components=[
                vm.Button(
                    text="Click me!", description=vm.Tooltip(text="Button tooltip", icon="info"), variant="outlined"
                )
            ],
            variant="outlined",
        ),
        vm.Container(
            title="Button with extra success",
            components=[
                vm.Button(
                    text="Click me!",
                    description=vm.Tooltip(text="Button tooltip", icon="info"),
                    extra={"color": "success", "outline": True},
                )
            ],
            variant="outlined",
        ),
        vm.Container(
            title="Button with extra danger",
            components=[
                vm.Button(
                    text="Click me!",
                    description=vm.Tooltip(text="Button tooltip", icon="info"),
                    extra={"color": "danger", "outline": True},
                )
            ],
            variant="outlined",
        ),
        vm.Container(
            title="Graph",
            components=[
                vm.Graph(
                    title="Graph 1",
                    figure=px.bar(
                        gapminder_2007,
                        x="continent",
                        y="lifeExp",
                        color="continent",
                    ),
                ),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(title="Test dashboard", pages=[page_1])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
