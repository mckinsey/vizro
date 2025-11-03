"""Example app.py to play with the fake vizro models."""

from typing import Literal, Union

from vizro.models._fake_vizro.models import (
    Action,
    Card,
    Component,
    Dashboard,
    ExportDataAction,
    Graph,
    Page,
    VizroBaseModel,
)


# User-defined custom components (realistic usage)
class CustomCard(VizroBaseModel):
    """User-defined custom component - demonstrates tree building issue."""

    type: Literal["custom_component"] = "custom_component"
    title: str


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
        Page(
            title="page_3",
            components=[Graph(figure="c3", actions=[Action(action="export", function=ExportDataAction(format="csv"))])],
        ),
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

# Minimal case demonstrating custom component tree building issue
dashboard_with_custom = Dashboard(
    pages=[
        Page(
            title="test_page",
            components=[
                Graph(figure="test_figure", actions=[]),  # Built-in component - appears in tree
                Card(text="test_card"),  # Built-in component - appears in tree
                CustomCard(title="custom_card"),  # Custom component - MISSING from tree
            ],
        ),
    ],
)

dashboard_with_custom = Dashboard.model_validate(dashboard_with_custom, context={"build_tree": True})
print("\n" + "=" * 80)
print("Tree output - CustomCard should now appear:")
print("=" * 80)
dashboard_with_custom._tree.print(repr="{node.kind} -> {node.data.type} (id={node.data.id})")
print("\n" + "=" * 80)

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

# JSON Schema (commented out to focus on tree building issue)
# graph = Graph(id="graph-id", figure="a", actions=[Action(id="action-id", action="a")])
# graph = Graph.model_validate(graph)
# print(json.dumps(graph.model_dump(), indent=2))
# print(json.dumps(ExportDataAction.model_json_schema(), indent=2))
# print("=" * 100)
# print(json.dumps(Card.model_json_schema(), indent=2))
# print("=" * 100)
# print(json.dumps(Dashboard.model_json_schema(), indent=2))
# print("=" * 100)
# print(json.dumps(SubComponent.model_json_schema(), indent=2))
# print("=" * 100)
# ea = ExportDataAction(format="csv")
# print(json.dumps(ea.model_dump(), indent=2))


"""


Run this file to see the error:
  $ hatch run python src/vizro/models/_fake_vizro/app.py
"""
