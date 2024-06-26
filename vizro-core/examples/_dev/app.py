"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

df = px.data.iris()

"""
Figures legend:

G - vm.Graph

A - vm.AgGrid
Ap - vm.AgGrid with pagination=True

T - vm.Table
Tp - vm.Table with pagination=True

================================================================

Combinations to test:

1.
G, G
G, G

2.
G, A
A, G

3.
G, T
T, G

4.
G, Ap,
Ap, G

5.
G, Tp
Tp, G
"""


page_1 = vm.Page(
    title="Title misalignment: G, G / G, G",
    layout=vm.Layout(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Graph(figure=px.scatter(df, title="Title Graph 1", x="sepal_width", y="sepal_length", color="species")),
        vm.Graph(figure=px.scatter(df, title="Title Graph 2", x="sepal_width", y="sepal_length", color="species")),
        vm.Graph(figure=px.scatter(df, title="Title Graph 3", x="sepal_width", y="sepal_length", color="species")),
        vm.Graph(figure=px.scatter(df, title="Title Graph 4", x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)

page_2 = vm.Page(
    title="Title misalignment: G, A / A, G",
    layout=vm.Layout(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Graph(figure=px.scatter(df, title="Title Graph 1", x="sepal_width", y="sepal_length", color="species")),
        vm.AgGrid(figure=dash_ag_grid(df), title="Title AgGrid 1"),
        vm.AgGrid(figure=dash_ag_grid(df), title="Title AgGrid 2"),
        vm.Graph(figure=px.scatter(df, title="Title Graph 2", x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)

page_3 = vm.Page(
    title="Title misalignment: G, T / T, G",
    layout=vm.Layout(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Graph(figure=px.scatter(df, title="Title Graph 1", x="sepal_width", y="sepal_length", color="species")),
        vm.Table(figure=dash_data_table(df), title="Title Table 1"),
        vm.Table(figure=dash_data_table(df), title="Title Table 2"),
        vm.Graph(figure=px.scatter(df, title="Title Graph 2", x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)

page_4 = vm.Page(
    title="Title misalignment: G, Ap / Ap, G",
    layout=vm.Layout(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Graph(figure=px.scatter(df, title="Title Graph 1", x="sepal_width", y="sepal_length", color="species")),
        vm.AgGrid(figure=dash_ag_grid(df, dashGridOptions={"pagination": True}), title="Title AgGrid 1"),
        vm.AgGrid(figure=dash_ag_grid(df, dashGridOptions={"pagination": True}), title="Title AgGrid 2"),
        vm.Graph(figure=px.scatter(df, title="Title Graph 2", x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)


page_5 = vm.Page(
    title="Title misalignment: G, Tp / Tp, G",
    layout=vm.Layout(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Graph(figure=px.scatter(df, title="Title Graph 1", x="sepal_width", y="sepal_length", color="species")),
        vm.Table(figure=dash_data_table(df, page_size=10), title="Title Table 1"),
        vm.Table(figure=dash_data_table(df, page_size=10), title="Title Table 2"),
        vm.Graph(figure=px.scatter(df, title="Title Graph 2", x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4, page_5])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
