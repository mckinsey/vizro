import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

df = px.data.iris()

page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])

from dash_auth import BasicAuth

USER_PWD = {
    "username": "password",
}

app = Vizro().build(dashboard)
BasicAuth(app.dash, USER_PWD, secret_key="<PUT SOMETHING SUPER SECRET HERE>")
app.run()
