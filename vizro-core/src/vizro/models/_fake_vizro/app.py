"""Example app.py to play with the fake vizro models."""

from vizro.models._fake_vizro.models import Dashboard, Graph, Page


class CustomPage(Page):
    # Allow int
    title: int


class CustomGraph(Graph):
    figure: int


# If the above custom components subclass VizroBaseModel instead of Page/Graph then behaviour should be the same (
# unlike it is now).
graph_1 = Graph(figure="a")
custom_graph_1 = CustomGraph(figure=2)

graph_2 = Graph(figure="a")
custom_graph_2 = CustomGraph(figure=2)

page = Page(title="Title", components=[graph_1, custom_graph_1])
custom_page = CustomPage(title=2, components=[graph_2, custom_graph_2])

# No add_type needed anywhere!!

dashboard = Dashboard(pages=[page, custom_page])
dashboard = Dashboard.model_validate(dashboard)

assert type(dashboard.pages[0]) is Page
assert type(dashboard.pages[1]) is CustomPage
assert type(dashboard.pages[0].components[0]) is Graph
assert type(dashboard.pages[0].components[1]) is CustomGraph
assert type(dashboard.pages[1].components[0]) is Graph
assert type(dashboard.pages[1].components[1]) is CustomGraph

###
# YAML configuration
# Must have type specified since it's a real discriminated union:
graph_1 = dict(figure="a", type="graph")  # , type="graph"
# Can't specify type since it's not a real discriminated union. There's no way of doing a custom component like this
# (this is currently possible thanks to add_type but in docs we say it's not possible so it's ok to break).
# Comment MS: I think "don't have to" is a better term than "can't"?? I think it works if one specifies the type!
page = dict(title="Title", components=[graph_1])

dashboard = Dashboard(pages=[page])
dashboard = Dashboard.model_validate(dashboard)

assert type(dashboard.pages[0]) is Page
assert type(dashboard.pages[0].components[0]) is Graph

###
# Try other models
## THIS NOW WORKS ALREADY :) (as in that it DOESNT pass validation)
# The reason is (I think) because `revalidate_instances` essentially dumps the model, it gets a type, and the type will
# then mismatch
dashboard_wrong = Dashboard(pages=[graph_1])
# dashboard_wrong_dict = {
#     "pages": [{"title": 1, "components": [graph_1, custom_graph_1]}],
# }
# dashboard_wrong = Dashboard.model_validate(dashboard_wrong_dict)
