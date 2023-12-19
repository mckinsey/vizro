from typing import List

from asserts import assert_component_equal
from vizro.models import VizroBaseModel
from dash import html


class X(VizroBaseModel):
    text: str

    def build(self):
        return html.Div(
            [html.H1("Heading"), html.P(self.text, id=self.id), html.Hr(), html.H2("Something")], className="blah"
        )


class Y(VizroBaseModel):
    children: List[X]

    def build(self):
        return html.Div([child.build() for child in self.children], id=self.id, className="container")


def test_X_build():
    # Test for low-level contents.
    result = X(id="x", text="Hello world").build()
    expected = html.Div(
        [html.H1("Heading"), html.P("Hello world", id="x"), html.Hr(), html.H2("Something")], className="blah"
    )
    assert_component_equal(result, expected)


def test_Y_build():
    # Test for higher-level container.
    many_x = [X(text="Hello world") for _ in range(4)]
    result = Y(id="y", children=many_x).build()
    # We don't want to compare the whole component tree here. Instead compare the bit that's specifically in Y and
    # ignore the children:
    assert_component_equal(result, html.Div(id="y", className="container"), keys_to_strip={"children"})
    # And also compare the "interface" between X and Y:
    assert all(isinstance(child, html.Div) for child in result.children)
