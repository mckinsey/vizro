"""Example app.py to play with the fake vizro models."""

import json
from typing import Union

from vizro.models._fake_vizro.models import Action, Card, Component, Dashboard, Graph, Page, VizroBaseModel


class CustomPage(Page):
    # Allow int
    title: int


class CustomPageBase(VizroBaseModel):
    title: int
    components: list[Union[Graph, Card]]


class CustomGraph(Graph):
    figure: int


class CustomGraphBase(VizroBaseModel):
    figure: int


dashboard = Dashboard(
    pages=[
        Page(title="page_1", components=[Component(x="c1")]),
        Page(title="page_2", components=[Graph(figure="c3", actions=[Action(action="action1")])]),
    ]
)

# dashboard_data = {
#     "pages": [
#         {
#             "title": "page_1",
#             "components": [
#                 {"type": "graph", "figure": "c1"},
#                 {"type": "card", "text": "some text for card"},
#             ],
#         },
#         {
#             "title": "page_2",
#             "components": [
#                 {"type": "graph", "figure": "c3"},
#                 # You can add another Card or Graph here if desired
#             ],
#         },
#     ],
# }

# dashboard = Dashboard.model_validate(dashboard, context={"build_tree": True})
# print("--------------------------------")
# for page in dashboard.pages:
#     page.pre_build()
# Notes
# Any additional model validate erases private property of tree, but why does it
# NOT erase the _parent_model attribute
# print("--------------------------------")
# dashboard = Dashboard.model_validate(dashboard)

# comp = Component.from_pre_build(
#     {"x": [SubComponent(y="new c3"), SubComponent(y="another new c3")]}, dashboard.pages[0], "components"
# )
# dashboard._tree.print(repr="{node.data.type} (id={node.data.id})")

# dashboard.pages[0]._tree.print()  # repr="{node.data.type} (id={node.data.id})"
# dashboard.pages[0]._tree.print()  # repr="{node.data.type} (id={node.data.id})"
# print("---")
# print(dashboard.pages[0].components[0].actions[0])
# print(dashboard.pages[0].components[0].actions[0]._parent_model)

# JSON Schema
graph = Graph(id="graph-id", figure="a", actions=[Action(id="action-id", action="a")])
# graph = Graph.model_validate(graph)
print(json.dumps(graph.model_dump(), indent=2))
