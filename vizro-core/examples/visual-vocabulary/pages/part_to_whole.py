"""Part-to-whole charts."""

import vizro.models as vm

from pages._factories import waterfall_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file
from pages.examples import donut, funnel, pie, stacked_bar, stacked_column, treemap

pie_page = vm.Page(
    title="Pie",
    path="part-to-whole/pie",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a pie chart?

            A pie chart is a circular chart divided into segments to show proportions and percentages between
            categories. The circle represents the whole.

            &nbsp;

            #### When should I use it?

            Use the pie chart when you need to show your audience a quick view of how data is distributed
            proportionately, with percentages highlighted. The different values you present must add up to a total and
            equal 100%.

            The downsides are that pie charts tend to occupy more space than other charts, they don't
            work well with more than a few values because labeling small segments is challenging, and it can be
            difficult to accurately compare the sizes of the segments.
        """
        ),
        vm.Graph(figure=pie.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("pie.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("pie.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

donut_page = vm.Page(
    title="Donut",
    path="part-to-whole/donut",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a donut chart?

            A donut chart looks like a pie chart, but has a blank space in the center which may contain additional
            information.

            &nbsp;

            #### When should I use it?

            A donut chart can be used in place of a pie chart, particularly when you are short of space or have extra
            information you would like to share about the data. It may also be more effective if you wish your audience
            to focus on the length of the arcs of the sections instead of the proportions of the segment sizes.
        """
        ),
        vm.Graph(figure=donut.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("donut.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("donut.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

treemap_page = vm.Page(
    title="Treemap",
    path="part-to-whole/treemap",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

                #### What is a treemap?

                A treemap shows hierarchical data arranged as a set of nested rectangles: rectangles are sized
                proportionately to the quantity they represent, combined together to form larger parent category
                rectangles.

                &nbsp;

                #### When should I use it?

                It's helpful to use a treemap when you wish to display hierarchical part-to-whole relationships. You can
                compare groups and single elements nested within them. Consider using them instead of Pie charts when
                you have a higher number of categories. Treemaps are very compact and allow audiences to get a quick
                overview of the data.
            """
        ),
        vm.Graph(figure=treemap.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("treemap.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("treemap.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

stacked_bar_page = vm.Page(
    title="Stacked bar",
    path="part-to-whole/stacked-bar",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a stacked bar chart?

            A stacked bar chart displays bars divided into segments, with each segment's length proportional to the
            value it represents. One axis shows the categories being compared, while the other provides a value scale
            starting from zero. The segments within each bar are stacked on top of each other, allowing for a cumulative
            comparison.

            &nbsp;

            #### When should I use it?

            Use a stacked bar chart to help your audience compare the total sizes of categories as well as the
            individual components within those categories. This chart type is ideal for visualizing part-to-whole
            relationships and identifying patterns within categorical data. Ensure clear labeling for each segment,
            especially when there are many categories, and consider using a legend or abbreviations with fuller
            descriptions below.
        """
        ),
        vm.Graph(figure=stacked_bar.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("stacked_bar.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("stacked_bar.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

stacked_column_page = vm.Page(
    title="Stacked column",
    path="part-to-whole/stacked-column",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a stacked column chart?

            A stacked column chart displays columns divided into segments, with each segment's height proportional to
            the value it represents. One axis shows the categories being compared, while the other provides a value
            scale starting from zero. The segments within each column are stacked on top of each other, allowing for a
            cumulative comparison.

            &nbsp;

            #### When should I use it?

            Use a stacked column chart to help your audience compare the total sizes of categories as well as the
            individual components within those categories. This chart type is ideal for visualizing part-to-whole
            relationships and identifying patterns within categorical data. Ensure clear labeling for each segment,
            especially when there are many categories, and consider using a legend or abbreviations with fuller
            descriptions below.
        """
        ),
        vm.Graph(figure=stacked_column.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("stacked_column.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("stacked_column.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

funnel_page = vm.Page(
    title="Funnel",
    path="part-to-whole/funnel",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a funnel chart?

            A funnel area chart is a type of data visualization that represents stages in a process, with the size of
            each area proportional to its value. The chart typically narrows as it progresses, visually depicting the
            reduction in numbers through each stage. One axis represents the stages of the process, while the other axis
            indicates the values or quantities at each stage.

            &nbsp;

            #### When should I use it?

            Use a funnel area chart to help your audience understand and compare the progression of data through
            different stages of a process. This chart type is particularly effective for visualizing conversion rates,
            sales processes, or any sequential data where you want to highlight drop-offs or reductions between stages.
        """
        ),
        vm.Graph(figure=funnel.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("funnel.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("funnel.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

waterfall_page = waterfall_factory("part-to-whole")

pages = [donut_page, pie_page, treemap_page, stacked_bar_page, stacked_column_page, funnel_page, waterfall_page]
