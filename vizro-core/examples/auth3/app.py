from typing import Literal, Annotated

from dash import set_props
from dash_auth import BasicAuth, protected
import plotly.graph_objs as go
from pydantic import Tag

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
import dash_bootstrap_components as dbc

from vizro.models.types import capture

# This is what a user without permission sees instead of the scatter plot:
forbidden_graph = go.Figure(
    layout={
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "annotations": [
            {
                "text": "You don't have permission to see this graph",
                "xref": "paper",
                "yref": "paper",
            }
        ],
    }
)


# set_props has some limitations but actually should work pretty well here. It means you can update something outside
# the Dash outputs without needing to modify the callback at all.
# https://dash.plotly.com/advanced-callbacks#setting-properties-directly
# Note unauthenticated_output is always run within the context of a callback (assuming you never do
# ProtectedGraph.__call__ outside a callback, which Vizro doesn't by default).
def unauthenticated_output():
    set_props("auth_modal", {"is_open": True})
    return forbidden_graph


class ProtectedGraph(vm.Graph):
    # The unauthenticated response could be made different for different graphs by adding an unauthenticated_output field.
    # Here it's the same forbidden_graph always.
    @protected(unauthenticated_output, groups=["admin"])
    def __call__(self, **kwargs):
        return super().__call__()


df = px.data.iris()

page = vm.Page(
    title="My first dashboard",
    components=[
        ProtectedGraph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])


USER_PWD = {
    "username": "password",
    "admin": "password",
}

USER_GROUPS = {"username": ["user"], "admin": ["admin"]}

app = Vizro().build(dashboard)

# This is the lazy way to insert a dbc.Modal into the layout without needing to do a whole new CustomDashboard model.
app.dash.layout.children.append(
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Access denied")),
            dbc.ModalBody("You don't have permission to see some things on this page"),
        ],
        centered=True,
        id="auth_modal",
    )
)

BasicAuth(app.dash, USER_PWD, user_groups=USER_GROUPS, secret_key="<PUT SOMETHING SUPER SECRET HERE>")
app.run()
