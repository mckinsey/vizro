"""Example app.py to play with the fake vizro models."""

from typing import Union

from vizro.models._fake_vizro.models import Card, Graph, Page, VizroBaseModel


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
