"""Contains custom components and charts used inside the dashboard."""

import vizro.models as vm
import vizro.plotly.express as px

from ._charts import CodeClipboard, FlexContainer, Markdown

gapminder = px.data.gapminder()
iris = px.data.iris()
stocks = px.data.stocks()
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
        vm.Graph(
            figure=px.scatter(
                iris, x="sepal_width", y="sepal_length", color="species"
            )
        ),
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
