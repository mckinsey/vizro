"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.models.types import capture


iris = px.data.iris()
tips = px.data.tips()
gapminder = px.data.gapminder().query("year==2007")


@capture("ag_grid")
def my_custom_ag_grid(data_frame, chosen_columns, **kwargs):
    print(f"\nChosen column: {chosen_columns}\n")
    return dash_ag_grid(data_frame=data_frame[chosen_columns], **kwargs)()


page = vm.Page(
    title="Fix empty dropdown as parameter",
    layout=vm.Layout(grid=[[0, 1], [2, 2]]),
    components=[
        vm.Card(text="This is a test to fix the empty dropdown as parameter."),
        vm.Card(text="This is a test to fix the empty dropdown as parameter.", href="https://www.google.com"),
        vm.AgGrid(
            id="my_custom_ag_grid",
            figure=my_custom_ag_grid(
                data_frame=iris,
                chosen_columns=iris.columns.to_list(),
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["my_custom_ag_grid.chosen_columns"],
            selector=vm.Dropdown(
                title="Choose columns",
                options=iris.columns.to_list(),
                multi=True,
            ),
        ),
    ],
)

page_two = vm.Page(
    title="Graph",
    layout=vm.Layout(grid=[[2, 2], [0, 1]]),
    components=[
        vm.Graph(
            figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
        ),
        vm.Graph(
            figure=px.histogram(
                tips,
                x="day",
                y="total_bill",
                color="sex",
                barmode="group",
                category_orders={"day": ["Thur", "Fri", "Sat", "Sun"]},
            )
        ),
        vm.Graph(figure=px.scatter(gapminder, x="gdpPercap", y="lifeExp", size="pop", size_max=60)),
    ],
)

dashboard = vm.Dashboard(pages=[page, page_two])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
