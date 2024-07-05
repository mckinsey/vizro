"""Contains custom components and charts used inside the dashboard."""

import vizro.models as vm
import vizro.plotly.express as px

from ._charts import CodeClipboard, FlexContainer, Markdown

gapminder = px.data.gapminder()
iris = px.data.iris()
stocks = px.data.stocks()
tips = px.data.tips()

vm.Page.add_type("components", CodeClipboard)
vm.Page.add_type("components", FlexContainer)
vm.Container.add_type("components", Markdown)

# CHART PAGES -------------------------------------------------------------
line = vm.Page(
    title="Line",
    layout=vm.Layout(
        grid=[[0, 0, 0, 0, 0]] * 1 + [[1, 1, 1, 2, 2]] * 2,
    ),
    components=[
        vm.Card(
            text="""

            #### What is a Line?

            A Line chart presents a series of data points over a continuous interval or time period, joined together with straight lines.

            &nbsp;

            #### When to use it?

            You should select a Line chart when you want to show trends and invite analysis of how the data has changed
            over time. Usually, your y-axis will show a quantitative value and your x-axis will be marked as a timescale
            or a sequence of intervals. You can also display negative values below the x-axis. If you wish to group
            several lines (different data series) in the same chart, try to limit yourself to 3-4 to avoid cluttering
            up your chart and making it harder for the audience to read.
        """
        ),
        vm.Graph(figure=px.line(stocks, x="date", y="GOOG")),
        CodeClipboard(
            text="""
               ```python
               import vizro.models as vm
               import vizro.plotly.express as px
               from vizro import Vizro

               gapminder = px.data.gapminder()

               page = vm.Page(
                   title="Line",
                   components=[
                       vm.Graph(
                            figure=px.line(stocks, x="date", y="GOOG")
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


scatter = vm.Page(
    title="Scatter",
    layout=vm.Layout(
        grid=[[0, 0, 0, 0, 0]] * 1 + [[1, 1, 1, 2, 2]] * 2,
    ),
    components=[
        vm.Card(
            text="""

            #### What is a scatter?

            A scatter plot is a two-dimensional data visualisation using dots to represent the values obtained for two different variables - one plotted along the x-axis and the other plotted along the y-axis.

            &nbsp;

            #### When to use it?

            Use Scatter Plots when you want to show the relationship between two variables. Scatter plots are sometimes called Correlation plots because they show how two variables are correlated. Scatter plots are ideal when you have paired numerical data and you want to see if one variable impacts the other. However, do remember that correlation is not causation, and another unnoticed variable may be influencing results. Make sure your audience does not draw the wrong conclusions.
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
                               iris, x="sepal_width", y="sepal_length", color="species"
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

bar = vm.Page(
    title="Bar",
    layout=vm.Layout(
        grid=[[0, 0, 0, 0, 0]] * 1 + [[1, 1, 1, 2, 2]] * 2,
    ),
    components=[
        vm.Card(
            text="""

            #### What is a bar chart?

            A Bar chart displays bars in lengths proportional to the values they represent. One axis of
            the chart shows the categories to compare and the other axis provides a value scale,
            starting with zero.

            &nbsp;

            #### When to use the bar chart?

            Select a Bar chart when you want to help your audience draw size comparisons and identify
            patterns between categorical data, i.e., data that presents **how many?** in each category. You can
            arrange your bars in any order to fit the message you wish to emphasise. Be mindful of labelling
            clearly when you have a large number of bars. You may need to include a legend,
            or use abbreviations in the chart with fuller descriptions below of the terms used.

        """
        ),
        vm.Graph(
            figure=px.bar(
                data_frame=tips.groupby("day").agg({"total_bill": "sum"}).reset_index(),
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

               page = vm.Page(
                   title="Bar",
                   components=[
                     vm.Graph(
            figure=px.bar(data_frame=tips.groupby("day").agg({"total_bill": "sum"}).reset_index(), x="total_bill", y="day",orientation="h")
        )
                   ]
               )

               dashboard = vm.Dashboard(pages=[page])
               Vizro().build(dashboard).run()
               ```

               """
        ),
    ],
)


column = vm.Page(
    title="Column",
    layout=vm.Layout(
        grid=[[0, 0, 0, 0, 0]] * 1 + [[1, 1, 1, 2, 2]] * 2,
    ),
    components=[
        vm.Card(
            text="""

            #### What is a column chart?

            A Column chart is a vertical Bar chart, with column lengths varying according to the
            categorical value they represent. The scale is presented on the y-axis, starting with zero.

            &nbsp;

            #### When to use the column chart?

            Select a Column chart when you want to help your audience draw size comparisons and identify
            patterns between categorical data, i.e., data that presents `how many?` in each category. You can
            arrange your columns in any order to fit the message you wish to emphasise. Be mindful of
            labelling clearly when you have a large number of columns. You may need to include a legend,
            or use abbreviations in the chart with fuller descriptions below of the terms used.

        """
        ),
        vm.Graph(
            figure=px.bar(
                data_frame=gapminder.query("country == 'China'"),
                x="year",
                y="gdpPercap",
            )
        ),
        CodeClipboard(
            text="""
               ```python
               import vizro.models as vm
               import vizro.plotly.express as px
               from vizro import Vizro

               gapminder = px.data.gapminder()

               page = vm.Page(
                   title="Column",
                   components=[
                      vm.Graph(
                          figure=px.bar(
                              data_frame=gapminder.query("country == 'China'"), x="year", y="gdpPercap"
                          )
                      )
                   ]
               )

               dashboard = vm.Dashboard(pages=[page])
               Vizro().build(dashboard).run()
               ```

               """
        ),
    ],
)


pie = vm.Page(
    title="Pie",
    layout=vm.Layout(
        grid=[[0, 0, 0, 0, 0]] * 1 + [[1, 1, 1, 2, 2]] * 2,
    ),
    components=[
        vm.Card(
            text="""

            #### What is a pie chart?

            A Pie chart is a circular chart divided into segments to show proportions and percentages between categories. The circle represents the whole.
            
            &nbsp;

            #### When to use the chart?

            Use the Pie chart when you need to show your audience a quick view of how data is distributed proportionately, with percentages highlighted. The different values you present must add up to a total and equal 100%.

            The downsides are that Pie charts tend to occupy more space than many other charts, they don’t work well with more than a few values because labelling small segments is challenging, and it can be difficult to accurately compare the sizes of the segments.

        """
        ),
        vm.Graph(
            figure=px.pie(
                data_frame=tips,
                values='tip', names='day',
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
                            values='tip', names='day',
                          )
                      )
                   ]
               )

               dashboard = vm.Dashboard(pages=[page])
               Vizro().build(dashboard).run()
               ```

               """
        ),
    ],
)
