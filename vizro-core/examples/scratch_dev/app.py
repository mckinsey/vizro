import numpy as np
import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash_ag_grid import AgGrid
from vizro import Vizro
from vizro.models.types import capture
from vizro.managers import data_manager

df = px.data.iris()
df['date_column'] = pd.date_range(start=pd.to_datetime('2024-01-01'), periods=len(df), freq='D')
df['is_setosa'] = df['species'] == 'setosa'

data_manager["static_df"] = df
data_manager["dynamic_df"] = lambda number_of_points=10: df.head(number_of_points)


SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}


page_1 = vm.Page(
    title="Single/Multi static DD",
    components=[
        vm.Graph(
            figure=px.scatter(
                "static_df", x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            )
        )
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(multi=True)),
        vm.Filter(column="species", selector=vm.Dropdown(multi=False)),
    ],
)

page_2 = vm.Page(
    title="Single/Multi dynamic DD",
    components=[
        vm.Graph(
            id="graph_2",
            figure=px.scatter(
                "dynamic_df", x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        )
    ],
    controls=[
        # TODO-REVIEWER: To a bug with the standard _build_dynamic_placeholder:
        #  1. Replace vm.Dropdown._build_dynamic_placeholder with vm.Checklist._build_dynamic_placeholder implementation
        #  2. Run the app and open page_2
        #  3. Select values ["setosa", "versicolor"] in the multi Dropdown, and "versicolor" in the single Dropdown
        #  4. Refresh the page.
        vm.Filter(column="species", selector=vm.Dropdown(multi=True)),
        vm.Filter(column="species", selector=vm.Dropdown(multi=False)),
        vm.Parameter(
            targets=["graph_2.data_frame.number_of_points"], selector=vm.Slider(min=10, max=150, step=10, value=10)
        ),
    ],
)


long_df = pd.DataFrame(
    {
        # TODO-UI: By setting max width of the Dropdown seems like option height is automatically adjusted.
        "long_string": [
            # List of 100 strings with variable number (1 -> 101) of characters "A"(95%) or space " "(5%).
            "Value " + "".join(" " if np.random.rand() < 0.05 else "A" for _ in range(length))
            for length in range(1, 101)
        ],
        "x": range(1, 101),
        "y": range(101, 201),
    }
)

page_3 = vm.Page(
    title="Long values in Dropdown",
    components=[vm.Graph(figure=px.scatter(long_df, x="x", y="y"))],
    controls=[vm.Filter(column="long_string")],
)

page_4 = vm.Page(
    title="All selectors",
    components=[
        vm.Graph(
            figure=px.scatter(
                "static_df", x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            )
        )
    ],
    controls=[
        vm.Filter(column="species", selector=vm.RadioItems(title="RadioItems Single")),
        vm.Filter(column="species", selector=vm.Dropdown(multi=False, title="Dropdown Single")),
        vm.Filter(column="species", selector=vm.Dropdown(multi=True, title="Dropdown Multi")),
        vm.Filter(column="species", selector=vm.Checklist(title="Checklist Multi")),
        vm.Filter(column="is_setosa", selector=vm.Switch(title="Switch Single")),
        vm.Filter(column="sepal_width", selector=vm.Slider(min=2, max=5, step=0.1, title="Slider Single")),
        vm.Filter(column="sepal_length", selector=vm.RangeSlider(min=4, max=8, step=0.1, title="Range Slider")),
        vm.Filter(column="date_column", selector=vm.DatePicker(range=False, title="Single Dropdown")),
        vm.Filter(column="date_column", selector=vm.DatePicker(range=True, title="Range DatePicker")),
    ]
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4])
if __name__ == "__main__":
    Vizro().build(dashboard).run()
