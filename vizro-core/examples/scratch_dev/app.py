import vizro.models as vm
import vizro.plotly.express as px
from nutree import IterMethod
from vizro import Vizro
from vizro.managers import model_manager

gapminder = px.data.gapminder().query("year == 2007")

page = vm.Page(
    title="Page Title",
    # description="Longer description of the page content",
    components=[
        vm.Graph(
            id="sunburst", figure=px.sunburst(gapminder, path=["continent", "country"], values="pop", color="lifeExp")
        )
    ],
    # controls=[
    #     vm.Filter(column="continent"),
    #     vm.Parameter(targets=["sunburst.color"], selector=vm.RadioItems(options=["lifeExp", "pop"], title="Color")),
    # ],
)

dashboard = vm.Dashboard(id="dashboard", pages=[page])
app = Vizro().build(dashboard)

# print(model_manager["sunburst"])
# model_manager.print_dashboard_tree()

# for node in model_manager._ModelManager__dashboard_tree.iterator(method=IterMethod.POST_ORDER):
#     print(node.data.__class__.__name__, node.data.id)

# vm.VizroBaseModel.from_dict_in_build(parent_id="dashboard", field_name="pages", data={"id": "test_model"})

model_manager.print_dashboard_tree()

# app.run()
