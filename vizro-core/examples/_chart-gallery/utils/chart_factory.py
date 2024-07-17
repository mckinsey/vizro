"""Contains reusable page functions to create identical content with a different `id`.

Note: Since each page can only belong to one navigation group, we need a new page with a unique ID for
each chart type used in different groups.
"""

import vizro.models as vm
import vizro.plotly.express as px

from ._page_utils import DATA_DICT, PAGE_GRID
from .custom_extensions import CodeClipboard, butterfly


def line_factory(id: str, title: str):
    """Reusable function to create the page content for the line chart with a unique ID."""
    return vm.Page(
        id=id,
        title=title,
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""

            #### What is a line chart?

            A line chart presents a series of data points over a continuous interval or time period, joined together
            with straight lines.

            &nbsp;

            #### When to use it?

            You should select a line chart when you want to show trends over time. Usually, your y-axis will show a
            quantitative value and your x-axis will be marked as a timescale or a sequence of intervals. You can also
            display negative values below the x-axis. If you wish to group several lines (different data series) in the
            same chart, try to limit yourself to 3-4 to avoid cluttering up your chart.
        """
            ),
            vm.Graph(figure=px.line(DATA_DICT["stocks"], x="date", y="GOOG")),
            CodeClipboard(
                text="""
                ```python
                import vizro.models as vm
                import vizro.plotly.express as px
                from vizro import Vizro

                stocks = px.data.stocks()

                page = vm.Page(
                    title="Line",
                    components=[
                        vm.Graph(
                            figure=px.line(
                                stocks, x="date", y="GOOG"
                            )
                        )
                    ],
                )

                dashboard = vm.Dashboard(pages=[page])
                Vizro().build(dashboard).run()
                ```
                """
            ),
        ],
    )


def scatter_factory(id: str, title: str):
    """Reusable function to create the page content for the scatter chart with a unique ID."""
    return vm.Page(
        id=id,
        title=title,
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""

            #### What is a scatter chart?

            A scatter plot is a two-dimensional data visualization using dots to represent the values obtained for two
            different variables - one plotted along the x-axis and the other plotted along the y-axis.

            &nbsp;

            #### When to use it?

            Use scatter plots when you want to show the relationship between two variables. Scatter plots are sometimes
            called Correlation plots because they show how two variables are correlated. Scatter plots are ideal when
            you have paired numerical data and you want to see if one variable impacts the other. However, do remember
            that correlation is not causation. Make sure your audience does not draw the wrong conclusions.
        """
            ),
            vm.Graph(figure=px.scatter(DATA_DICT["iris"], x="sepal_width", y="sepal_length", color="species")),
            CodeClipboard(
                text="""
               ```python
               import vizro.models as vm
               import vizro.plotly.express as px
               from vizro import Vizro

               iris = px.data.iris()

               page = vm.Page(
                   title="Scatter",
                   components=[
                       vm.Graph(
                           figure=px.scatter(
                               iris,
                               x="sepal_width",
                               y="sepal_length",
                               color="species",
                           )
                       )
                   ],
               )

               dashboard = vm.Dashboard(pages=[page])
               Vizro().build(dashboard).run()
               ```
               """
            ),
        ],
    )


def bar_factory(id: str, title: str):
    """Reusable function to create the page content for the bar chart with a unique ID."""
    return vm.Page(
        id=id,
        title=title,
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""

            #### What is a bar chart?

            A bar chart displays bars in lengths proportional to the values they represent. One axis of
            the chart shows the categories to compare and the other axis provides a value scale,
            starting with zero.

            &nbsp;

            #### When to use it?

            Select a bar chart when you want to help your audience draw size comparisons and identify
            patterns between categorical data, i.e., data that presents **how many?** in each category. You can
            arrange your bars in any order to fit the message you wish to emphasize. Be mindful of labeling
            clearly when you have a large number of bars. You may need to include a legend,
            or use abbreviations in the chart with fuller descriptions below of the terms used.

        """
            ),
            vm.Graph(
                figure=px.bar(
                    data_frame=DATA_DICT["tips_agg"],
                    x="total_bill",
                    y="day",
                    orientation="h",
                )
            ),
            CodeClipboard(
                text="""
                ```python
                import vizro.models as vm
                import vizro.plotly.express as px
                from vizro import Vizro

                tips = px.data.tips()
                tips_agg = (
                    tips.groupby("day")
                    .agg({"total_bill": "sum"})
                    .sort_values("total_bill")
                    .reset_index()
                )

                page = vm.Page(
                    title="Bar",
                    components=[
                        vm.Graph(
                            figure=px.bar(
                                data_frame=tips_agg,
                                x="total_bill",
                                y="day",
                                orientation="h",
                            )
                        )
                    ],
                )

                dashboard = vm.Dashboard(pages=[page])
                Vizro().build(dashboard).run()
                ```
                """
            ),
        ],
    )


def column_factory(id: str, title: str):
    """Reusable function to create the page content for the column chart with a unique ID."""
    return vm.Page(
        id=id,
        title=title,
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""

            #### What is a column chart?

            A column chart is a vertical bar chart, with column lengths varying according to the
            categorical value they represent. The scale is presented on the y-axis, starting with zero.

            &nbsp;

            #### When to use it?

            Select a column chart when you want to help your audience draw size comparisons and identify
            patterns between categorical data, i.e., data that presents **how many?** in each category. You can
            arrange your columns in any order to fit the message you wish to emphasize. Be mindful of
            labeling clearly when you have a large number of columns. You may need to include a legend,
            or use abbreviations in the chart with fuller descriptions below of the terms used.
        """
            ),
            vm.Graph(
                figure=px.bar(
                    data_frame=DATA_DICT["tips_agg"],
                    y="total_bill",
                    x="day",
                )
            ),
            CodeClipboard(
                text="""
                ```python
                import vizro.models as vm
                import vizro.plotly.express as px
                from vizro import Vizro

                tips = px.data.tips()
                tips_agg = (
                    tips.groupby("day")
                    .agg({"total_bill": "sum"})
                    .sort_values("total_bill")
                    .reset_index()
                )

                page = vm.Page(
                    title="Column",
                    components=[
                        vm.Graph(
                            figure=px.bar(
                                data_frame=tips_agg,
                                y="total_bill",
                                x="day",
                            )
                        )
                    ],
                )

                dashboard = vm.Dashboard(pages=[page])
                Vizro().build(dashboard).run()
                ```
                """
            ),
        ],
    )


def treemap_factory(id: str, title: str):
    """Reusable function to create the page content for the treemap chart with a unique ID."""
    return vm.Page(
        id=id,
        title=title,
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""

                #### What is a treemap?

                A treemap shows hierarchical data arranged as a set of nested rectangles: rectangles sized
                proportionately to the quantity they represent, combining together to form larger **parent**
                category rectangles.

                &nbsp;

                #### When to use it?

                It's helpful to use a treemap when you wish to display hierarchical part-to-whole relationships. You can
                compare groups and single elements nested within them. Consider using them instead of Pie charts when
                you have a higher number of categories. Treemaps are very compact and allow audiences to get a quick
                overview of the data.
            """
            ),
            vm.Graph(
                figure=px.treemap(
                    DATA_DICT["gapminder_2007"],
                    path=[px.Constant("world"), "continent", "country"],
                    values="pop",
                    color="lifeExp",
                )
            ),
            CodeClipboard(
                text="""
                    ```python
                    import vizro.models as vm
                    import vizro.plotly.express as px
                    from vizro import Vizro

                    gapminder = px.data.gapminder()
                    gapminder_2007 = gapminder.query("year == 2007")

                    page = vm.Page(
                        title="Treemap",
                        components=[
                            vm.Graph(
                                figure=px.treemap(
                                    gapminder_2007,
                                    path=[px.Constant("world"), "continent", "country"],
                                    values="pop",
                                    color="lifeExp",
                                )
                            ),
                        ],
                    )

                    dashboard = vm.Dashboard(pages=[page])
                    Vizro().build(dashboard).run()
                    ```
                    """
            ),
        ],
    )


def butterfly_factory(id: str, title: str):
    """Reusable function to create the page content for the butterfly chart with a unique ID."""
    return vm.Page(
        id=id,
        title=title,
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""

                #### What is a butterfly chart?

                A butterfly chart (also called a tornado chart) is a bar chart for displaying two sets of data series
                side by side.

                &nbsp;

                #### When to use it?

                Use a butterfly chart when you wish to emphasize the comparison between two data sets sharing the same
                parameters. Sharing this chart with your audience will help them see at a glance how two groups differ
                within the same parameters. You can also **stack** two bars on each side if you wish to divide your
                categories.
            """
            ),
            vm.Graph(figure=butterfly(DATA_DICT["ages"], x1="Male", x2="Female", y="Age")),
            CodeClipboard(
                text="""
                    ```python
                    import vizro.models as vm
                    from vizro import Vizro
                    import pandas as pd
                    from vizro.models.types import capture
                    import plotly.graph_objects as go

                    ages = pd.DataFrame(
                        {
                            "Age": ["0-19", "20-29", "30-39", "40-49", "50-59", ">=60"],
                            "Male": [800, 2000, 4200, 5000, 2100, 800],
                            "Female": [1000, 3000, 3500, 3800, 3600, 700],
                        }
                    )


                    @capture("graph")
                    def butterfly(data_frame: pd.DataFrame, x1: str, x2: str, y: str):
                        fig = go.Figure()
                        fig.add_trace(
                            go.Bar(
                                x=-data_frame[x1].values, y=data_frame[y], orientation="h", name=x1,
                            )
                        )
                        fig.add_trace(
                            go.Bar(x=data_frame[x2], y=data_frame[y], orientation="h", name=x2,)
                        )
                        fig.update_layout(barmode="relative")
                        return fig


                    dashboard = vm.Dashboard(
                        pages=[
                            vm.Page(
                                title="Butterfly",
                                components=[
                                    vm.Graph(
                                        figure=butterfly(ages, x1="Male", x2="Female", y="Age")
                                    )
                                ],
                            )
                        ]
                    )
                    Vizro().build(dashboard).run()
                    ```
                    """
            ),
        ],
    )
