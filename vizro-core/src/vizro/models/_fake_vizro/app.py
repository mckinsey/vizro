"""Example app.py to play with the fake vizro models."""

from typing import Union

from vizro.models._fake_vizro.models import Card, Dashboard, Graph, Page, VizroBaseModel


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
        Page(title="page_1", components=[Graph(figure="c1"), Card(text="some text for card")]),
        Page(title="page_2", components=[Graph(figure="c3")]),
    ]
)

dashboard_data = {
    "pages": [
        {
            "title": "page_1",
            "components": [
                {"type": "graph", "figure": "c1"},
                {"type": "card", "text": "some text for card"},
            ],
        },
        {
            "title": "page_2",
            "components": [
                {"type": "graph", "figure": "c3"},
                # You can add another Card or Graph here if desired
            ],
        },
    ],
}

dashboard = Dashboard.model_validate(dashboard_data, context={"build_tree": True})
dashboard._tree.print()
