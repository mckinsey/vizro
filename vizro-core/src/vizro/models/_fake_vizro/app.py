"""Example app.py to play with the fake vizro models."""

from typing import Union

from vizro.models._fake_vizro.models import Card, Component, Dashboard, Graph, Page, VizroBaseModel


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
        # Page(title="page_2", components=[Component(x=[SubComponent(y="c3")])]),
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

dashboard = Dashboard.model_validate(dashboard, context={"build_tree": True})
for page in dashboard.pages:
    page.pre_build()


# comp = Component.from_pre_build(
#     {"x": [SubComponent(y="new c3"), SubComponent(y="another new c3")]}, dashboard.pages[0], "components"
# )
# dashboard._tree.print(repr="{node.data.type} (id={node.data.id})")

dashboard.pages[0]._tree.print()  # repr="{node.data.type} (id={node.data.id})"
