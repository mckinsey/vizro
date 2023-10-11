"""Unit tests for vizro.models.RadioItems."""
import json

import plotly
import pytest
from dash import dcc, html
from pydantic import ValidationError

from vizro.models._action._action import Action
from vizro.models._components.form import RadioItems


@pytest.fixture()
def expected_radio_items():
    return html.Div(
        [
            html.P("Title"),
            dcc.RadioItems(
                id="radio_items_id",
                options=["A", "B", "C"],
                value="A",
                className="selector_body_radio_items",
                persistence=True,
            ),
        ],
        className="selector_container",
        id="radio_items_id_outer",
    )


class TestRadioItemsInstantiation:
    """Tests model instantiation."""

    def test_create_radio_items_mandatory_only(self):
        radio_items = RadioItems()

        assert hasattr(radio_items, "id")
        assert radio_items.type == "radio_items"
        assert radio_items.options == []
        assert radio_items.value is None
        assert radio_items.title is None
        assert radio_items.actions == []

    def test_create_radio_items_mandatory_and_optional(self):
        radio_items = RadioItems(options=["A", "B", "C"], value="A", title="Title", id="radio_items_id")

        assert radio_items.id == "radio_items_id"
        assert radio_items.type == "radio_items"
        assert radio_items.options == ["A", "B", "C"]
        assert radio_items.value == "A"
        assert radio_items.title == "Title"
        assert radio_items.actions == []

    @pytest.mark.parametrize(
        "test_options, expected",
        [
            (["A", "B", "C"], ["A", "B", "C"]),
            ([1, 2, 3], [1.0, 2.0, 3.0]),
            ([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]),
            ([True, False, True], [True, False, True]),
            (
                [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}],
                [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}],
            ),
            (
                [{"label": "New York", "value": "NYC"}, {"label": "Berlin", "value": "BER"}],
                [{"label": "New York", "value": "NYC"}, {"label": "Berlin", "value": "BER"}],
            ),
            (
                [{"label": "True", "value": True}, {"label": "False", "value": False}],
                [{"label": "True", "value": True}, {"label": "False", "value": False}],
            ),
            ([True, 2.0, 1.0, "A", "B"], ["True", "2.0", "1.0", "A", "B"]),
        ],
    )
    def test_create_radio_items_valid_options(self, test_options, expected):
        radio_items = RadioItems(options=test_options)

        assert hasattr(radio_items, "id")
        assert radio_items.type == "radio_items"
        assert radio_items.options == expected
        assert radio_items.value is None
        assert radio_items.title is None
        assert radio_items.actions == []

    @pytest.mark.parametrize("test_options", [1, "A", True, 1.0])
    def test_create_radio_items_invalid_options_type(self, test_options):
        with pytest.raises(ValidationError, match="value is not a valid list"):
            RadioItems(options=test_options)

    def test_create_radio_items_invalid_options_dict(self):
        with pytest.raises(
            ValidationError,
            match="Invalid argument `options` passed. Expected a dict with keys `label` and `value`.",
        ):
            RadioItems(options=[{"hello": "A", "world": "A"}, {"hello": "B", "world": "B"}])

    @pytest.mark.parametrize(
        "test_value, options",
        [
            ("A", ["A", "B", "C"]),
            (1, [1, 2, 3]),
            (2.0, [1.0, 2.0, 3.0]),
            (True, [True, False]),
            ("B", [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}]),
            ("True", [True, 2.0, 1.0, "A", "B"]),
        ],
    )
    def test_create_radio_items_valid_value(self, test_value, options):
        radio_items = RadioItems(options=options, value=test_value)

        assert hasattr(radio_items, "id")
        assert radio_items.type == "radio_items"
        assert radio_items.value == test_value
        assert radio_items.title is None
        assert radio_items.actions == []

    @pytest.mark.parametrize(
        "test_value, options",
        [
            (5, ["A", "B", "C"]),
            (5, [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}]),
            ("D", ["A", "B", "C"]),
            ("D", [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}]),
            (True, ["A", "B", "C"]),
            (True, [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}]),
        ],
    )
    def test_create_radio_items_invalid_value_non_existing(self, test_value, options):
        with pytest.raises(ValidationError, match="Please provide a valid value from `options`."):
            RadioItems(value=test_value, options=options)

    def test_create_radio_items_invalid_value_format(self):
        with pytest.raises(ValidationError, match="3 validation errors for RadioItems"):
            RadioItems(value=[1], options=[1, 2, 3, 4, 5])

    def test_set_action_via_validator(self, test_action_function):
        radio_items = RadioItems(actions=[Action(function=test_action_function)])
        actions_chain = radio_items.actions[0]
        assert actions_chain.trigger.component_property == "value"


class TestRadioItemsBuild:
    """Tests model build method."""

    def test_radio_items_build(self, expected_radio_items):
        radio_items = RadioItems(options=["A", "B", "C"], id="radio_items_id", title="Title").build()

        result = json.loads(json.dumps(radio_items, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_radio_items, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected
