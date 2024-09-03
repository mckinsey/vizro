"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.tables import dash_ag_grid, dash_data_table

df = px.data.iris()

HEADER = """
Each point in the scatter plot represents one of the 150 iris flowers, with colors indicating their types. The Setosa
type is easily identifiable by its short and wide sepals.

However, there is still overlap between the Versicolor and Virginica types when considering only sepal width and length.
"""

FOOTER = """SOURCE: **Plotly Iris, 2024**"""


@capture("graph")
def scatter(data_frame, **kwargs):
    """Scatter plot."""
    fig = px.scatter(data_frame, **kwargs)
    fig.update_layout(margin_b=24, legend_y=-0.2, legend_title="")
    return fig


page = vm.Page(
    title="Fig Title",
    layout=vm.Layout(
        grid=[[0, 1, 2, 3]],
    ),
    components=[
        vm.Graph(figure=scatter(df, x="sepal_width", y="sepal_length")),
        vm.Graph(figure=scatter(df, x="sepal_width", y="sepal_length", title="Blah blah")),
        vm.Table(figure=dash_data_table(df), title="My Table"),
        vm.Graph(
            figure=scatter(df, x="sepal_width", y="sepal_length", title="My Graph <br><span>This is a subtitle</span>")
        ),
    ],
)
page_two = vm.Page(
    title="Graph Title",
    layout=vm.Layout(
        grid=[[0, 1, 2, 3]],
    ),
    components=[
        vm.Graph(figure=scatter(df, x="sepal_width", y="sepal_length")),
        vm.Graph(figure=scatter(df, x="sepal_width", y="sepal_length"), title="Blah blah"),
        vm.Table(figure=dash_data_table(df), title="My Table"),
        vm.Graph(
            figure=scatter(df, x="sepal_width", y="sepal_length", color="species"),
            title="My Graph",
            header=HEADER,
        ),
    ],
)

page_three = vm.Page(
    title="Styling Header/Footer",
    layout=vm.Layout(
        grid=[[0, 1, 2]],
    ),
    components=[
        vm.AgGrid(figure=dash_ag_grid(df), title="My AgGrid", header=HEADER, footer=FOOTER),
        vm.Table(figure=dash_data_table(df), title="My Table", header=HEADER, footer=FOOTER),
        vm.Graph(
            figure=scatter(df, x="sepal_width", y="sepal_length", color="species"),
            title="My Graph",
            header=HEADER,
            footer=FOOTER,
        ),
    ],
)

page_four = vm.Page(
    title="Styling Header/Footer - AgGrid",
    components=[
        vm.AgGrid(figure=dash_ag_grid(df), title="My AgGrid", header=HEADER, footer=FOOTER),
    ],
)

page_five = vm.Page(
    title="Styling Header/Footer - DataTable",
    components=[
        vm.Table(figure=dash_data_table(df), title="My AgGrid", header=HEADER, footer=FOOTER),
    ],
)


page_six = vm.Page(
    title="Styling Header/Footer - Graph",
    components=[
        vm.Graph(
            figure=scatter(df, x="sepal_width", y="sepal_length", color="species"),
            title="Relationships between Sepal Width and Sepal Length",
            header=HEADER,
            footer=FOOTER,
        ),
    ],
)


dashboard = vm.Dashboard(pages=[page, page_two, page_three, page_four, page_five, page_six])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
