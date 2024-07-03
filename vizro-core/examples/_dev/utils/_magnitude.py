"""Contains custom components and charts used inside the dashboard."""

import vizro.models as vm
import vizro.plotly.express as px

from ._charts import CodeClipboard, FlexContainer, CustomTextCard

gapminder = px.data.gapminder()
vm.Page.add_type("components", CodeClipboard)
vm.Page.add_type("components", FlexContainer)
vm.Container.add_type("components", CustomTextCard)

# CHART PAGES -------------------------------------------------------------
bar = vm.Page(
    title="Bar",
    layout=vm.Layout(
        grid=[[0, 0, 1, 1, 1]] * 3 + [[2, 2, 1, 1, 1]] * 4,
        col_gap="80px",
    ),
    components=[
        vm.Card(
            text="""

            ### What is a bar chart?

            A Bar chart displays bars in lengths proportional to the values they represent. One axis of
            the chart shows the categories to compare and the other axis provides a value scale,
            starting with zero.

            &nbsp;

            ### When to use the bar chart?

            Select a Bar chart when you want to help your audience draw size comparisons and identify
            patterns between categorical data, i.e., data that presents **how many?** in each category. You can
            arrange your bars in any order to fit the message you wish to emphasise. Be mindful of labelling
            clearly when you have a large number of bars. You may need to include a legend,
            or use abbreviations in the chart with fuller descriptions below of the terms used.

        """
        ),
        vm.Graph(
            figure=px.bar(data_frame=gapminder.query("country == 'China'"), y="year", x="lifeExp", orientation="h")
        ),
        CodeClipboard(
            text="""
               ```python
               import vizro.models as vm
               import vizro.plotly.express as px
               from vizro import Vizro

               gapminder = px.data.gapminder()

               page = vm.Page(
                   title="Bar",
                   components=[
                      vm.Graph(figure=px.bar(data_frame=gapminder.query("country == 'Germany'"), x="year", y="pop"))
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
        grid=[[0, 0, 1, 1, 1]] * 3 + [[2, 2, 1, 1, 1]] * 4,
        col_gap="80px",
    ),
    components=[
        vm.Card(
            text="""

            ### What is a column chart?

            A Column chart is a vertical Bar chart, with column lengths varying according to the
            categorical value they represent. The scale is presented on the y-axis, starting with zero.

            &nbsp;

            ### When to use the column chart?

            Select a Column chart when you want to help your audience draw size comparisons and identify
            patterns between categorical data, i.e., data that presents `how many?` in each category. You can
            arrange your columns in any order to fit the message you wish to emphasise. Be mindful of
            labelling clearly when you have a large number of columns. You may need to include a legend,
            or use abbreviations in the chart with fuller descriptions below of the terms used.

        """
        ),
        vm.Graph(figure=px.bar(data_frame=gapminder.query("country == 'China'"), x="year", y="lifeExp")),
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
                      vm.Graph(figure=px.bar(data_frame=gapminder.query("country == 'China'"), x="year", y="pop"))
                   ]
               )

               dashboard = vm.Dashboard(pages=[page])
               Vizro().build(dashboard).run()
               ```

               """
        ),
    ],
)
