"""Contains custom components and charts used inside the dashboard."""

import vizro.models as vm
import vizro.plotly.express as px

from ._components import CodeClipboard, FlexContainer, Markdown

PAGE_GRID = [[0, 0, 0, 0, 0]] * 2 + [[1, 1, 1, 2, 2]] * 5

gapminder = px.data.gapminder()
iris = px.data.iris()
stocks = px.data.stocks()
tips = px.data.tips()
tips_agg = tips.groupby("day").agg({"total_bill": "sum"}).sort_values("total_bill").reset_index()

vm.Page.add_type("components", CodeClipboard)
vm.Page.add_type("components", FlexContainer)
vm.Container.add_type("components", Markdown)


# All functions ending with `_factory` are there to re-use the existing content of a page. Given the restriction that
# one page can only be mapped to one navigation group, we have to create a new page with a new ID.
def line_factory(id: str, title: str):
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
            vm.Graph(figure=px.line(stocks, x="date", y="GOOG")),
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
            vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),
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
                    data_frame=tips_agg,
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
                    data_frame=tips_agg,
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


# PAGES -------------------------------------------------------------
line = line_factory("Line", "Line")
time_line = line_factory("Time-Line", "Line")
time_column = column_factory("Time-Column", "Column")
scatter = scatter_factory("Scatter", "Scatter")
bar = bar_factory("Bar", "Bar")
ordered_bar = bar_factory("Ordered Bar", "Ordered Bar")
column = column_factory("Column", "Column")
ordered_column = column_factory("Ordered Column", "Ordered Column")


pie = vm.Page(
    title="Pie",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a pie chart?

            A pie chart is a circular chart divided into segments to show proportions and percentages between
            categories. The circle represents the whole.

            &nbsp;

            #### When to use it?

            Use the pie chart when you need to show your audience a quick view of how data is distributed
            proportionately, with percentages highlighted. The different values you present must add up to a total and
            equal 100%.

            The downsides are that pie charts tend to occupy more space than other charts, they don`t
            work well with more than a few values because labeling small segments is challenging, and it can be
            difficult to accurately compare the sizes of the segments.
        """
        ),
        vm.Graph(
            figure=px.pie(
                data_frame=tips,
                values="tip",
                names="day",
            )
        ),
        CodeClipboard(
            text="""
                ```python
                import vizro.models as vm
                import vizro.plotly.express as px
                from vizro import Vizro

                tips = px.data.tips()

                page = vm.Page(
                    title="Pie",
                    components=[
                        vm.Graph(
                            figure=px.pie(
                                data_frame=tips,
                                values="tip",
                                names="day",
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


donut = vm.Page(
    title="Donut",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a donut chart?

            A donut chart looks like a pie chart, but has a blank space in the center which may contain additional
            information.

            &nbsp;

            #### When to use it?

            A donut chart can be used in place of a pie chart, particularly when you are short of space or have extra
            information you would like to share about the data. It may also be more effective if you wish your audience
            to focus on the length of the arcs of the sections instead of the proportions of the segment sizes.
        """
        ),
        vm.Graph(
            figure=px.pie(
                data_frame=tips,
                values="tip",
                names="day",
                hole=0.4,
            )
        ),
        CodeClipboard(
            text="""
                ```python
                import vizro.models as vm
                import vizro.plotly.express as px
                from vizro import Vizro

                tips = px.data.tips()

                page = vm.Page(
                    title="Donut",
                    components=[
                        vm.Graph(
                            figure=px.pie(
                                data_frame=tips,
                                values="tip",
                                names="day",
                                hole=0.4,
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


boxplot = vm.Page(
    title="Boxplot",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a boxplot?

            A Box Plot (also known as a Box and Whisker Plot) provides a visual display of multiple datasets,
            indicating the median (center) and the range of the data for each.

            &nbsp;

            #### When to use it?

            Choose a Box Plot when you need to summarize distributions between many groups or datasets. It takes up
            less space than many other charts.

            Create boxes to display the median, and the upper and lower quartiles. Add `whiskers` to highlight
            variability outside the upper and lower quartiles. You can add outliers as dots beyond, but in line with
            the whiskers.

        """
        ),
        vm.Graph(
            figure=px.box(
                data_frame=tips,
                y="total_bill",
                x="day",
                color="day",
            )
        ),
        CodeClipboard(
            text="""
               ```python
               import vizro.models as vm
               import vizro.plotly.express as px
               from vizro import Vizro

               tips = px.data.tips()

               page = vm.Page(
                   title="Boxplot",
                   components=[
                       vm.Graph(
                            figure=px.boxplot(
                                data_frame=tips,
                                y='total_bill', x='day', color='day',
                            )
                        ),
                   ]
               )

               dashboard = vm.Dashboard(pages=[page])
               Vizro().build(dashboard).run()
               ```

               """
        ),
    ],
)


violin = vm.Page(
    title="Violin",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a violin?

            A Violin Plot is similar to a Box Plot, but works better for visualizing more complex distributions and
            their probability density at different values.

            &nbsp;

            #### When to use it?

            Use this chart to go beyond the simple Box Plot and show the distribution shape of the data, the
            inter-quartile range, the confidence intervals and the median.
        """
        ),
        vm.Graph(
            figure=px.violin(
                data_frame=tips,
                y="total_bill",
                x="day",
                color="day",
            )
        ),
        CodeClipboard(
            text="""
               ```python
               import vizro.models as vm
               import vizro.plotly.express as px
               from vizro import Vizro

               tips = px.data.tips()

               page = vm.Page(
                   title="Violin",
                   components=[
                       vm.Graph(
                            figure=px.violin(
                                data_frame=tips,
                                y='total_bill', x='day', color='day',
                            )
                        ),
                   ]
               )

               dashboard = vm.Dashboard(pages=[page])
               Vizro().build(dashboard).run()
               ```

               """
        ),
    ],
)
