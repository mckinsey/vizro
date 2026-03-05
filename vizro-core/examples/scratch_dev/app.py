"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px

from vizro import Vizro

df = px.data.iris()

page_1 = vm.Page(
    title="Page One",
    layout=vm.Flex(),
    components=[vm.Card(text="placeholder")],
)


page_two = vm.Page(
    title="Page Two",
    controls=[vm.Filter(column="species")],
    components=[
        vm.Graph(figure=px.histogram(df, x="sepal_length")),
    ],
)

page_three = vm.Page(
    title="Page Three",
    controls=[
        vm.Filter(
            column="species",
            # visible=False,
        )
    ],
    components=[
        vm.Graph(figure=px.histogram(df, x="sepal_length")),
    ],
)

navigation = vm.Navigation(
    nav_selector=vm.NavBar(
        # pages=["Page One", "Page Two", "Page Three"],
        # pages={
        #     "First": ["Page One", "Page Two"],
        #     "Second": ["Page Three"]
        # },
        items=[
            vm.NavLink(pages=["Page One", "Page Two"], label="First Tab"),
            vm.NavLink(pages=["Page Three"], label="Second Tab"),
        ],
        position="top",
    ),
)

dashboard = vm.Dashboard(
    pages=[page_1, page_two, page_three],
    navigation=navigation,
    title="QB",
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
