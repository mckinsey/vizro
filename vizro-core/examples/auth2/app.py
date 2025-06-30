from dash_auth import BasicAuth, protected
import plotly.graph_objs as go
import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
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


class ProtectedGraph(vm.Graph):
    # The unauthenticated response could be made different for different graphs by adding an unauthenticated_output field.
    # Here it's the same forbidden_graph always.
    @protected(forbidden_graph, groups=["admin"])
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
BasicAuth(app.dash, USER_PWD, user_groups=USER_GROUPS, secret_key="<PUT SOMETHING SUPER SECRET HERE>")
app.run()
