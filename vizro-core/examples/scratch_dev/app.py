"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro

gapminder = px.data.gapminder().query("continent == 'Europe' and year == 2007")


page = vm.Page(
    title="Test page",
    components=[
        vm.Card(
            text="Card with all components",
            title="Card title",
            header="This is card header",
            footer="This is card footer",
            description="Tooltip",
        ),
        vm.Card(
            title="Card title",
            text="Card with just title",
        ),
        vm.Card(
            header="This is card header",
            text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.",
        ),
        vm.Card(
            text="Card without header",
            title="Card title",
            footer="This is card footer",
            description="Tooltip",
        ),
        vm.Graph(
            figure=px.bar(
                gapminder,
                x="country",
                y="lifeExp",
            )
        ),
        vm.Graph(
            figure=px.bar(
                gapminder,
                x="country",
                y="pop",
            )
        ),
    ],
    layout=vm.Grid(
        grid=[
            [0, 1, 2, 3],
            [4, 4, 5, 5],
            [4, 4, 5, 5],
            [4, 4, 5, 5],
        ]
    ),
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
