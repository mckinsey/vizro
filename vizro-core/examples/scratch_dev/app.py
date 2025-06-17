from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm
import pandas as pd
from vizro.tables import dash_ag_grid

gapminder_2007 = px.data.gapminder().query("year == 2007")

# Create a list of fake long words
long_words = [
    "Client Discussion",
    "Client Discussion Engagement",
    "Completed Engagement",
    "Confirmed Engagement in Progress",
    "Inactive/on hold",
]

# Create the DataFrame
df = pd.DataFrame({"id": range(1, 6), "category": ["A", "B", "A", "C", "B"], "long_words": long_words})


page_1 = vm.Page(
    title="Test page",
    components=[
        vm.Container(
            components=[vm.AgGrid(figure=dash_ag_grid(df))],
            variant="outlined",
            controls=[
                vm.Filter(column="long_words"),
                vm.Filter(
                    column="category",
                    selector=vm.Dropdown(
                        options=[
                            {"label": "a", "value": "A"},
                            {"label": "b", "value": "B"},
                            {"label": "c", "value": "C"},
                        ]
                    ),
                ),
                vm.Filter(column="id"),
            ],
        ),
    ],
    controls=[
        vm.Filter(column="long_words"),
    ],
)


page_2 = vm.Page(
    title="Test page 2",
    components=[
        vm.Container(
            components=[vm.AgGrid(figure=dash_ag_grid(df))],
            variant="outlined",
            controls=[
                vm.Filter(column="long_words"),
                vm.Filter(
                    column="category",
                    selector=vm.Dropdown(
                        options=[
                            {"label": "a", "value": "A"},
                            {"label": "b", "value": "B"},
                            {"label": "c", "value": "C"},
                        ]
                    ),
                ),
                vm.Filter(column="id"),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(title="Test dashboard", pages=[page_1, page_2], 
                          navigation=vm.Navigation(
        pages={"Group A": ["Test page"], "Group B": ["Test page 2"]}, nav_selector=vm.NavBar()
    ),)

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
