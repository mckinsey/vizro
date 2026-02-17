import numpy as np
import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager

df = px.data.iris()
df["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(df), freq="D")
df["is_setosa"] = df["species"] == "setosa"

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
        ),
        vm.Container(
            title="Container title",
            components=[
                vm.Graph(
                    figure=px.scatter(
                        "static_df",
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        color_discrete_map=SPECIES_COLORS,
                    )
                ),
            ],
            controls=[
                vm.Filter(column="species", selector=vm.Dropdown(multi=True)),
            ],
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(multi=False, variant="plain")),
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
            targets=["graph_2.data_frame.number_of_points"], selector=vm.Slider(min=10, max=150, step=20, value=10)
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
    title="All dynamic selectors",
    components=[
        vm.Container(
            controls=[
                vm.Filter(column="species", selector=vm.RadioItems(title="RadioItems Single")),
                vm.Filter(column="species", selector=vm.Dropdown(multi=False, title="Dropdown Single")),
                vm.Filter(column="species", selector=vm.Dropdown(multi=True, title="Dropdown Multi")),
                vm.Filter(column="species", selector=vm.Checklist(title="Checklist Multi")),
                vm.Filter(column="is_setosa", selector=vm.Switch(title="Switch Single")),
                vm.Filter(column="sepal_width", selector=vm.Slider(title="Slider Single")),
                vm.Filter(column="sepal_length", selector=vm.RangeSlider(title="Range Slider")),
                vm.Filter(column="date_column", selector=vm.DatePicker(range=False, title="Single Dropdown")),
                vm.Filter(column="date_column", selector=vm.DatePicker(range=True, title="Range DatePicker")),
            ],
            components=[
                vm.Graph(
                    id="graph_4",
                    figure=px.scatter(
                        "dynamic_df",
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        color_discrete_map=SPECIES_COLORS,
                    ),
                )
            ],
        )
    ],
    controls=[
        vm.Parameter(
            targets=["graph_4.data_frame.number_of_points"],
            selector=vm.Slider(min=10, max=150, step=20, value=150, title="DataFrame Parameter"),
        ),
        vm.Filter(column="species", selector=vm.RadioItems(title="RadioItems Single")),
        vm.Filter(column="species", selector=vm.Dropdown(multi=False, title="Dropdown Single")),
        vm.Filter(column="species", selector=vm.Dropdown(multi=True, title="Dropdown Multi")),
        vm.Filter(column="species", selector=vm.Checklist(title="Checklist Multi")),
        vm.Filter(column="is_setosa", selector=vm.Switch(title="Switch Single")),
        vm.Filter(column="sepal_width", selector=vm.Slider(title="Slider Single")),
        vm.Filter(column="sepal_length", selector=vm.RangeSlider(title="Range Slider")),
        vm.Filter(column="date_column", selector=vm.DatePicker(range=False, title="Single Dropdown")),
        vm.Filter(column="date_column", selector=vm.DatePicker(range=True, title="Range DatePicker")),
    ],
)

page_5 = vm.Page(
    title="Sliders stress-test",
    components=[
        vm.Container(
            controls=[
                vm.Filter(column="sepal_length", selector=vm.RangeSlider(title="No Config")),
                vm.Filter(column="sepal_length", selector=vm.RangeSlider(min=0, max=10, title="Min/Max")),
                vm.Filter(
                    column="sepal_length", selector=vm.RangeSlider(min=0.13, max=10.13, title="Min-flot/Max-float")
                ),
                vm.Filter(column="sepal_length", selector=vm.RangeSlider(step=1, title="Step")),
                vm.Filter(column="sepal_length", selector=vm.RangeSlider(step=0.5, title="Step-float")),
                vm.Filter(
                    column="sepal_length",
                    selector=vm.RangeSlider(marks={5: "5", 6.1: "6.1", 7.2: "7.2"}, title="Marks"),
                ),
                vm.Filter(
                    column="sepal_length", selector=vm.RangeSlider(min=0, max=10, step=0.5, title="Min/Max/Step-float")
                ),
                vm.Filter(
                    column="sepal_length",
                    selector=vm.RangeSlider(min=0.13, max=10.13, step=1, title="Min-float/Max-float/Step"),
                ),
                vm.Filter(
                    column="sepal_length",
                    selector=vm.RangeSlider(min=0.13, max=10.13, step=0.5, title="Min-float/Max-float/Step-float"),
                ),
                vm.Filter(
                    column="sepal_length",
                    selector=vm.RangeSlider(min=0, max=10, marks={0: "0", 5: "5", 10: "10"}, title="Min/Max/Marks"),
                ),
                vm.Filter(
                    column="sepal_length",
                    selector=vm.RangeSlider(
                        min=0.13,
                        max=10.13,
                        marks={0.13: "0.13", 5.13: "5.13", 10.13: "10.13"},
                        title="Min-float/Max-float/Marks-float",
                    ),
                ),
                vm.Filter(
                    column="sepal_length",
                    selector=vm.RangeSlider(
                        min=0, max=10, step=1, marks={0: "0", 5: "5", 10: "10"}, title="Min/Max/Step/Marks"
                    ),
                ),
                vm.Filter(
                    column="sepal_length",
                    selector=vm.RangeSlider(
                        min=0.13,
                        max=10.13,
                        step=0.5,
                        marks={0.13: "0.13", 5.13: "5.13", 10.13: "10.13"},
                        title="Min-float/Max-float/Step-float/Marks-float",
                    ),
                ),
            ],
            components=[
                vm.Graph(
                    id="graph_5",
                    figure=px.scatter(
                        "dynamic_df",
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        color_discrete_map=SPECIES_COLORS,
                    ),
                )
            ],
        )
    ],
    controls=[
        vm.Parameter(
            targets=["graph_5.data_frame.number_of_points"],
            selector=vm.Slider(min=10, max=150, step=20, value=10, title="DataFrame Parameter"),
        ),
        vm.Filter(column="sepal_length", selector=vm.Slider(title="No Config")),
        vm.Filter(column="sepal_length", selector=vm.Slider(min=0, max=10, title="Min/Max")),
        vm.Filter(column="sepal_length", selector=vm.Slider(min=0.13, max=10.13, title="Min-flot/Max-float")),
        vm.Filter(column="sepal_length", selector=vm.Slider(step=1, title="Step")),
        vm.Filter(column="sepal_length", selector=vm.Slider(step=0.5, title="Step-float")),
        vm.Filter(column="sepal_length", selector=vm.Slider(marks={5: "5", 6.1: "6.1", 7.2: "7.2"}, title="Marks")),
        vm.Filter(column="sepal_length", selector=vm.Slider(min=0, max=10, step=0.5, title="Min/Max/Step-float")),
        vm.Filter(
            column="sepal_length",
            selector=vm.Slider(min=0.13, max=10.13, step=1, title="Min-float/Max-float/Step"),
        ),
        vm.Filter(
            column="sepal_length",
            selector=vm.Slider(min=0.13, max=10.13, step=0.5, title="Min-float/Max-float/Step-float"),
        ),
        vm.Filter(
            column="sepal_length",
            selector=vm.Slider(min=0, max=10, marks={0: "0", 5: "5", 10: "10"}, title="Min/Max/Marks"),
        ),
        vm.Filter(
            column="sepal_length",
            selector=vm.Slider(
                min=0.13,
                max=10.13,
                marks={0.13: "0.13", 5.13: "5.13", 10.13: "10.13"},
                title="Min-float/Max-float/Marks-float",
            ),
        ),
        vm.Filter(
            column="sepal_length",
            selector=vm.Slider(min=0, max=10, step=1, marks={0: "0", 5: "5", 10: "10"}, title="Min/Max/Step/Marks"),
        ),
        vm.Filter(
            column="sepal_length",
            selector=vm.Slider(
                min=0.13,
                max=10.13,
                step=0.5,
                marks={0.13: "0.13", 5.13: "5.13", 10.13: "10.13"},
                title="Min-float/Max-float/Step-float/Marks-float",
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4, page_5])
if __name__ == "__main__":
    Vizro().build(dashboard).run()
