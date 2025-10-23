"""Unit tests for vizro.models.Card."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.actions as va
import vizro.models as vm


class TestCardInstantiation:
    """Tests model instantiation."""

    def test_create_card_mandatory_only(self):
        card = vm.Card(text="Text to test card")

        assert hasattr(card, "id")
        assert card.type == "card"
        assert card.text == "Text to test card"
        assert card.href == ""
        assert card._action_outputs == {
            "__default__": f"{card.id}-text.children",
            "text": f"{card.id}-text.children",
        }
        assert card._action_triggers == {"__default__": f"{card.id}-outer.n_clicks"}

    @pytest.mark.parametrize("href", ["/page_1_reference", "https://www.google.de/"])
    def test_create_card_mandatory_and_optional(self, href):
        card = vm.Card(
            id="card-id",
            text="Text to test card",
            href=href,
            header="Header",
            footer="Footer",
            description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
        )

        assert card.id == "card-id"
        assert card.type == "card"
        assert card.text == "Text to test card"
        assert card.header == "Header"
        assert card.footer == "Footer"
        assert card.href == href
        assert isinstance(card.description, vm.Tooltip)
        assert card._action_triggers == {"__default__": "card-id-outer.n_clicks"}
        assert card._action_outputs == {
            "__default__": "card-id-text.children",
            "text": "card-id-text.children",
            "header": "card-id_header.children",
            "footer": "card-id_footer.children",
            "description": "tooltip-id-text.children",
        }

    def test_mandatory_text_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Card()

    def test_none_as_text(self):
        with pytest.raises(ValidationError, match="Input should be a valid string"):
            vm.Card(text=None)

    def test_href_and_actions_defined(self):
        with pytest.raises(ValidationError, match=r"Card cannot have both `href` and `actions` defined."):
            vm.Card(text="Test", href="https://www.google.de/", actions=va.set_control(control="filter-1", value="A"))


class TestBuildMethod:
    """Tests build method."""

    def test_card_build_mandatory(self):
        card = vm.Card(id="card_id", text="Hello")
        card = card.build()
        expected_card = html.Div(
            id="card_id-outer",
            children=dbc.Card(
                id="card_id",
                children=[
                    None,
                    dbc.CardBody(
                        children=[
                            dcc.Markdown(
                                id="card_id-text", children="Hello", dangerously_allow_html=False, className="card-text"
                            ),
                            None,
                        ],
                        className="card-body-outer",
                    ),
                    None,
                ],
                class_name="",
            ),
            className="card-wrapper",
        )

        assert_component_equal(card, expected_card)

    def test_card_build_with_extra(self):
        """Test that extra arguments correctly override defaults."""
        card = vm.Card(id="card_id", text="Hello", extra={"class_name": "bg-primary p-1 mt-2 text-center h2"}).build()
        expected_card = html.Div(
            id="card_id-outer",
            children=dbc.Card(
                id="card_id",
                children=[
                    None,
                    dbc.CardBody(
                        children=[
                            dcc.Markdown(
                                id="card_id-text", children="Hello", dangerously_allow_html=False, className="card-text"
                            ),
                            None,
                        ],
                        className="card-body-outer",
                    ),
                    None,
                ],
                class_name="bg-primary p-1 mt-2 text-center h2",
            ),
            className="card-wrapper",
        )
        assert_component_equal(card, expected_card)

    def test_card_build_with_href(self):
        card = vm.Card(id="card_id", text="Hello", href="https://www.google.com")
        card = card.build()
        expected_card = html.Div(
            id="card_id-outer",
            children=dbc.Card(
                id="card_id",
                children=[
                    None,
                    dbc.CardBody(
                        children=[
                            dbc.NavLink(
                                dcc.Markdown(
                                    id="card_id-text",
                                    children="Hello",
                                    dangerously_allow_html=False,
                                    className="card-text",
                                ),
                                href="https://www.google.com",
                                target="_top",
                            ),
                            None,
                        ],
                        className="card-body-outer",
                    ),
                    None,
                ],
                class_name="card-nav",
            ),
            className="card-wrapper",
        )

        assert_component_equal(card, expected_card)

    def test_card_build_with_description_header(self):
        card = vm.Card(
            id="card_id",
            text="Hello",
            header="Card header",
            description=vm.Tooltip(text="Tooltip test", icon="Info", id="info"),
        )
        card = card.build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=dcc.Markdown("Tooltip test", id="info-text", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]

        expected_card = html.Div(
            id="card_id-outer",
            children=dbc.Card(
                id="card_id",
                children=[
                    dbc.CardHeader(
                        id="card_id_header",
                        children=html.Div(
                            children=[
                                dcc.Markdown(children="Card header", dangerously_allow_html=False),
                                *expected_description,
                            ],
                            className="card-header-outer",
                        ),
                    ),
                    dbc.CardBody(
                        children=[
                            dcc.Markdown(
                                id="card_id-text", children="Hello", dangerously_allow_html=False, className="card-text"
                            ),
                        ],
                        className="card-body-outer",
                    ),
                    None,
                ],
                class_name="",
            ),
            className="card-wrapper",
        )

        assert_component_equal(card, expected_card)

    def test_card_build_with_description_no_header(self):
        card = vm.Card(
            id="card_id",
            text="Hello",
            description=vm.Tooltip(text="Tooltip test", icon="Info", id="info"),
        )
        card = card.build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=dcc.Markdown("Tooltip test", id="info-text", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]

        expected_card = html.Div(
            id="card_id-outer",
            children=dbc.Card(
                id="card_id",
                children=[
                    None,
                    dbc.CardBody(
                        children=[
                            dcc.Markdown(
                                id="card_id-text", children="Hello", dangerously_allow_html=False, className="card-text"
                            ),
                            *expected_description,
                        ],
                        className="card-body-outer",
                    ),
                    None,
                ],
                class_name="",
            ),
            className="card-wrapper",
        )

        assert_component_equal(card, expected_card)

    def test_card_build_with_header_footer(self):
        card = vm.Card(id="card_id", text="Hello", header="Header", footer="Footer")
        card = card.build()
        expected_card = html.Div(
            id="card_id-outer",
            children=dbc.Card(
                id="card_id",
                children=[
                    dbc.CardHeader(
                        id="card_id_header",
                        children=html.Div(
                            children=[dcc.Markdown(children="Header", dangerously_allow_html=False), None],
                            className="card-header-outer",
                        ),
                    ),
                    dbc.CardBody(
                        children=[
                            dcc.Markdown(
                                id="card_id-text", children="Hello", dangerously_allow_html=False, className="card-text"
                            ),
                        ],
                        className="card-body-outer",
                    ),
                    dbc.CardFooter(
                        id="card_id_footer", children=dcc.Markdown(children="Footer", dangerously_allow_html=False)
                    ),
                ],
                class_name="",
            ),
            className="card-wrapper",
        )

        assert_component_equal(card, expected_card)

    @pytest.mark.parametrize(
        "test_text, expected",
        [
            ("""# Header""", "# Header"),
            ("""_This **tests** emphasis_""", "_This **tests** emphasis_"),
            ("""> This tests blockquotes""", "> This tests blockquotes"),
            ("""* This tests list items""", "* This tests list items"),
            ("Text to test card", "Text to test card"),
            ("", ""),
            (
                """![](assets/images/icons/content/hypotheses.svg)""",
                "![](assets/images/icons/content/hypotheses.svg)",
            ),
            ("""Code block: ```python print(1)```""", "Code block: ```python print(1)```"),
            ("""[Example page](/test_page)""", "[Example page](/test_page)"),
        ],
    )
    def test_markdown_setting(self, test_text, expected):
        card = vm.Card(id="id_valid", text=test_text)
        card = card.build()
        card_markdown = card["id_valid-text"]

        assert isinstance(card_markdown, dcc.Markdown)
        assert card_markdown.dangerously_allow_html is False
        assert card_markdown.children == expected

    @pytest.mark.parametrize(
        "test_text, expected",
        [
            ("""<p>Hello </p>""", "<p>Hello </p>"),  # html will not be evaluated but converted to string
            ("12345", "12345"),
            ("""$$ \\frac{1}{(\\sqrt{\\phi \\sqrt{5}}-\\phi)}$$""", "$$ \\frac{1}{(\\sqrt{\\phi \\sqrt{5}}-\\phi)}$$"),
        ],
    )
    def test_markdown_build_invalid(self, test_text, expected):
        card = vm.Card(id="test_id", text=test_text)
        card = card.build()
        card_markdown = card["test_id-text"]

        assert isinstance(card_markdown, dcc.Markdown)
        assert card_markdown.dangerously_allow_html is False
        assert card_markdown.children == expected
