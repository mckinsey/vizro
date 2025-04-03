"""Test app"""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

iris = px.data.iris()

page_home = vm.Page(
    title="Homepage",
    layout=vm.Layout(grid=[[0, 1], [2, 3]], row_gap="16px", col_gap="24px"),
    components=[
        vm.Card(
            text="""

                ### Components

                Main components of Vizro include **charts**, **tables**, **cards**, **figures**, **containers**,
                **buttons** and **tabs**.
                """,
            href="/page-one",
        ),
        vm.Card(
            text="""
                ### Controls

                Vizro has two different control types **Filter** and **Parameter**.

                You can use any pre-existing selector inside the **Filter** or **Parameter**:

                * Dropdown
                * Checklist
                * RadioItems
                * RangeSlider
                * Slider
                * DatePicker
                """,
            href="/page-two",
        ),
        vm.Card(
            text="""
                ### Actions

                Standard predefined actions are made available including **export data** and **filter interactions**.
                """,
            href="/page-one",
        ),
        vm.Card(
            text="""
                ### Extensions

                Vizro enables customization of **plotly express** and **graph object charts** as well as
                creating custom components based on Dash.
            """,
            href="/page-two",
        ),
    ],
)

page_one = vm.Page(
    title="Default",
    path="page-one",
    components=[vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"))],
    controls=[vm.Filter(column="species"), vm.Filter(column="petal_length"), vm.Filter(column="sepal_width")],
)

page_two = vm.Page(
    title="Styled containers",
    path="page-two",
    layout=vm.Layout(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Card(
            text="""
        ### Actions

        Standard predefined actions are made available including **export data** and **filter interactions**.
        """,
            href="/page-one",
        ),
        vm.Card(
            text="""
        ### Actions

        Standard predefined actions are made available including **export data** and **filter interactions**.
        """,
            href="/page-one",
        ),
        vm.Container(
            title="Container - filled",
            components=[vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"))],
            variant="filled",
        ),
        vm.Container(
            title="Container - outlined",
            components=[vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"))],
            variant="outlined",
        ),
    ],
    controls=[vm.Filter(column="species"), vm.Filter(column="petal_length")],
)

page_four = vm.Page(
    title="Card with Graph",
    components=[
        vm.Card(
            text="""
        ### Actions

        Standard predefined actions are made available including **export data** and **filter interactions**.
        """,
            href="/page-one",
        ),
        vm.Card(
            text="""
        ### Actions

        Standard predefined actions are made available including **export data** and **filter interactions**.
        """,
            href="/page-one",
        ),
        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
    ],
    controls=[vm.Filter(column="species"), vm.Filter(column="petal_length")],
)

dashboard = vm.Dashboard(pages=[page_home, page_one, page_two, page_four], title="Dashboard Title")

if __name__ == "__main__":
    Vizro().build(dashboard).run()
