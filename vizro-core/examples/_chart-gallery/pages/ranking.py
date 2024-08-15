"""Ranking charts."""

from typing import Optional

import vizro.models as vm
import vizro.plotly.express as px
from vizro.models.types import capture

from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file, tips


# AM comment: agreed that this is too complicated for such a simple example. In future we'll be able to do this post-fig
# update without needing a custom chart but for now let's just sort the values before passing to the plotting function.
# TODO: Move to custom_charts.py if we keep it
@capture("graph")
def ordered_histogram(data_frame, x: str, y: str, orientation: Optional[str] = None):
    """Custom bar chart function with ordered categories."""
    fig = px.histogram(data_frame, x=x, y=y, orientation=orientation)
    axis_update = fig.update_yaxes if orientation == "h" else fig.update_xaxes
    return axis_update(categoryorder="total descending")


ordered_bar = vm.Page(
    title="Ordered bar",
    path="ranking/ordered-bar",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is an ordered bar chart?

            An ordered bar chart displays bars with lengths proportional to their values, arranged in descending or
            ascending order. One axis shows the categories, and the other provides a value scale starting from zero.

            &nbsp;

            #### When should I use it?

            Use an ordered bar chart to help your audience compare sizes and identify patterns in categorical data,
            emphasizing the order of categories. This is ideal for showing rankings or priorities.
            Ensure clear labeling, especially with many bars, and consider using a legend or abbreviations with fuller
            descriptions below.
        """
        ),
        # AM comment: same as the bar chart but with sort_values.
        vm.Graph(
            figure=px.bar(
                px.data.gapminder().query("year == 2007 and pop > 1.5e8").sort_values("pop"),
                y="pop",
                x="country",
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

            #### What is an ordered column chart?

            An ordered column chart is a vertical bar chart where columns are arranged in descending or ascending order
            based on their values. The column lengths vary according to the categorical value they represent, with the
            scale on the y-axis starting from zero.

            &nbsp;

            #### When should I use it?

            Use an ordered column chart to help your audience compare sizes and identify patterns in categorical data,
            emphasizing the order of categories. This is ideal for showing rankings or progressions. Ensure clear
            labeling, especially with many columns, and consider using a legend or abbreviations with fuller
            descriptions below.
        """
        ),
        vm.Graph(
            figure=ordered_histogram(
                tips,
                y="total_bill",
                x="day",
            )
        ),
        make_code_clipboard_from_py_file("ordered_column.py"),
    ],
)


pages = [ordered_bar, ordered_column]
