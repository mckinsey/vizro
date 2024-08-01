"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card
from vizro.models.types import capture
from vizro.tables import dash_ag_grid, dash_data_table

df = px.data.iris()


# Graph
@capture("graph")
def my_graph_figure(data_frame, **kwargs):
    """My custom figure."""
    return px.scatter(data_frame, **kwargs)


class MyGraph(vm.Graph):
    """My custom class."""

    def build(self):
        """Custom build."""
        graph_build_obj = super().build()
        # DO SOMETHING
        return graph_build_obj


# Table
@capture("table")
def my_table_figure(data_frame, **kwargs):
    """My custom figure."""
    return dash_data_table(data_frame, **kwargs)()


class MyTable(vm.Table):
    """My custom class."""

    pass


# AgGrid
@capture("ag_grid")
def my_ag_grid_figure(data_frame, **kwargs):
    """My custom figure."""
    return dash_ag_grid(data_frame, **kwargs)()


class MyAgGrid(vm.AgGrid):
    """My custom class."""

    pass


# Figure
@capture("figure")
def my_kpi_card_figure(data_frame, **kwargs):
    """My custom figure."""
    return kpi_card(data_frame, **kwargs)()


class MyFigure(vm.Figure):
    """My custom class."""

    pass


# Action
@capture("action")
def my_action_function():
    """My custom action."""
    pass


class MyAction(vm.Action):
    """My custom class."""

    pass


page = vm.Page(
    title="Test",
    layout=vm.Layout(
        grid=[[0, 1], [2, 3], [4, 5], [6, 7], [8, -1]],
        col_gap="50px",
        row_gap="50px",
    ),
    components=[
        # Graph
        MyGraph(figure=px.scatter(df, x="sepal_width", y="sepal_length", title="My Graph")),
        MyGraph(figure=my_graph_figure(df, x="sepal_width", y="sepal_length", title="My Graph Custom Figure")),
        # Table
        MyTable(figure=dash_data_table(df), title="My Table"),
        MyTable(figure=my_table_figure(df), title="My Table Custom Figure"),
        # AgGrid
        MyAgGrid(figure=dash_ag_grid(df), title="My AgGrid"),
        MyAgGrid(figure=my_ag_grid_figure(df), title="My AgGrid Custom Figure"),
        # Figure
        MyFigure(figure=kpi_card(df, value_column="sepal_width", title="KPI Card")),
        MyFigure(figure=my_kpi_card_figure(df, value_column="sepal_width", title="KPI Card Custom Figure")),
        # Action
        MyGraph(
            figure=my_graph_figure(df, x="sepal_width", y="sepal_length", title="My Graph Custom Figure"),
            actions=[MyAction(function=my_action_function())],
        ),
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
