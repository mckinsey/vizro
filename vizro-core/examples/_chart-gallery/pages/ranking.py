import vizro.models as vm
import vizro.plotly.express as px
from utils._page_utils import DATA_DICT, PAGE_GRID, make_code_clipboard_from_py_file

ordered_bar = vm.Page(
    title="Ordered bar",
    path="ranking/ordered-bar",
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
        make_code_clipboard_from_py_file("ordered_bar.py"),
    ],
)


ordered_column = vm.Page(
    title="Ordered column",
    path="ranking/ordered-column",
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
        make_code_clipboard_from_py_file("ordered_column.py"),
    ],
)


pages = [ordered_bar, ordered_column]
