"""Demo to show how to use asserts. These are not real tests that are run as part of testing, just a teaching aid."""

from asserts import STRIP_ALL, assert_component_equal
from dash import html

from vizro.models import VizroBaseModel


class X(VizroBaseModel):
    # Low-level contents model.
    text: str

    def build(self):
        return html.Div(
            [html.H1("Heading"), html.P(self.text, id=self.id), html.Hr(), html.H2("Something")], className="inner"
        )


class Y(VizroBaseModel):
    # Higher-level container model.
    children: list[X]

    def build(self):
        return html.Div([child.build() for child in self.children], id=self.id, className="container")


def test_X_build():
    # Test for low-level contents: compare the whole component tree.
    # Sometimes setting keys_to_strip={"className"} is useful here.
    result = X(id="x", text="Hello world").build()
    expected = html.Div(
        [html.H1("Heading"), html.P("Hello world", id="x"), html.Hr(), html.H2("Something")], className="inner"
    )
    assert_component_equal(result, expected)


def test_Y_build():
    # Test for higher-level container.
    many_x = [X(text="Hello world") for _ in range(4)]
    result = Y(id="y", children=many_x).build()
    # We don't want to compare the whole component tree here. Instead compare the bit that's specifically in Y and
    # ignore the children:
    assert_component_equal(result, html.Div(id="y", className="container"), keys_to_strip={"children"})
    # And also compare the "interface" between X and Y. Use STRIP_ALL to not look at any properties of the html.Div.
    # This is basically the same as doing:
    # assert all(isinstance(child, html.Div) for child in result.children) and len(result.children) == 4
    assert_component_equal(result.children, [html.Div()] * 4, keys_to_strip=STRIP_ALL)
