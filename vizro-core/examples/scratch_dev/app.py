import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
from vizro.actions import set_control


df = px.data.iris()


page_1 = vm.Page(
    title="Buttons trigger set_control",
    layout=vm.Flex(),
    components=[
        vm.Button(
            text="Set setosa",
            actions=set_control(control="filter-id-1", value="setosa"),
        ),
        vm.Button(
            text="Set versicolor",
            actions=set_control(control="filter-id-1", value="versicolor"),
        ),
        vm.Button(
            text="Set virginica",
            actions=set_control(control="filter-id-1", value="virginica"),
        ),
        vm.Graph(
            id="graph-1",
            figure=px.scatter(
                df,
                x="sepal_width",
                y="sepal_length",
                color="species",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"},
            ),
        ),
    ],
    controls=[vm.Filter(id="filter-id-1", column="species", targets=["graph-1"])],
)

page_2 = vm.Page(
    title="Reset certain control example",
    components=[
        vm.Button(
            text="Reset species filter",
            actions=set_control(control="filter-id-2", value="setosa"),
        ),
        vm.Graph(
            id="graph-2",
            figure=px.scatter(
                df,
                x="sepal_width",
                y="sepal_length",
                color="species",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"},
            ),
        ),
    ],
    controls=[
        vm.Filter(id="filter-id-2", column="species", selector=vm.RadioItems()),
        vm.Filter(id="filter-id-3", column="sepal_length"),
    ],
)


dashboard = vm.Dashboard(pages=[page_1, page_2])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
