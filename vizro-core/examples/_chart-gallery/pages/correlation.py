import vizro.models as vm
import vizro.plotly.express as px
from utils._page_utils import DATA_DICT, PAGE_GRID, make_code_clipboard_from_py_file

scatter = vm.Page(
    title="Scatter",
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
        make_code_clipboard_from_py_file("scatter.py"),
    ],
)

pages = [scatter]