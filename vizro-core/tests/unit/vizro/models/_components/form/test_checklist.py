"""Unit tests for vizro.models.Checklist."""
import json

import plotly
import pytest
from dash import dcc, html
from pydantic import ValidationError

from vizro.models._action._action import Action
from vizro.models._components.form import Checklist


@pytest.fixture()
def expected_checklist():
    return html.Div(
        [
            html.P("Title"),
            dcc.Checklist(
                id="checklist_id",
                options=["ALL", "A", "B", "C"],
                value=["ALL"],
                className="selector_body_checklist",
                persistence=True,
            ),
        ],
        className="selector_container",
        id="checklist_id_outer",
    )


class TestChecklistInstantiation:
    """Tests model instantiation."""

    def test_create_checklist_mandatory_only(self):
        checklist = Checklist()

        assert hasattr(checklist, "id")
        assert checklist.type == "checklist"
        assert checklist.options == []
        assert checklist.value is None
        assert checklist.title is None
        assert checklist.actions == []

    def test_create_checklist_mandatory_and_optional(self):
        checklist = Checklist(options=["A", "B", "C"], value=["A"], title="Title", id="checklist-id")

        assert checklist.id == "checklist-id"
        assert checklist.type == "checklist"
        assert checklist.options == ["A", "B", "C"]
        assert checklist.value == ["A"]
        assert checklist.title == "Title"
        assert checklist.actions == []

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
    def test_create_checklist_valid_options(self, test_options, expected):
        checklist = Checklist(options=test_options)

        assert hasattr(checklist, "id")
        assert checklist.type == "checklist"
        assert checklist.options == expected
        assert checklist.value is None
        assert checklist.title is None
        assert checklist.actions == []

    @pytest.mark.parametrize("test_options", [1, "A", True, 1.0])
    def test_create_checklist_invalid_options_type(self, test_options):
        with pytest.raises(ValidationError, match="value is not a valid list"):
            Checklist(options=test_options)

    def test_create_checklist_invalid_options_dict(self):
        with pytest.raises(
            ValidationError,
            match="Invalid argument `options` passed. Expected a dict with keys `label` and `value`.",
        ):
            Checklist(options=[{"hello": "A", "world": "A"}, {"hello": "B", "world": "B"}])

    @pytest.mark.parametrize(
        "test_value, options",
        [
            (["A"], ["A", "B", "C"]),
            ([1, 2], [1, 2, 3]),
            ([1.0, 2.0], [1.0, 2.0, 3.0]),
            ([False, True], [True, False]),
            (["A", "B"], [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}]),
            (["True", "A"], [True, 2.0, 1.0, "A", "B"]),
        ],
    )
    def test_create_checklist_valid_value(self, test_value, options):
        checklist = Checklist(options=options, value=test_value)

        assert hasattr(checklist, "id")
        assert checklist.type == "checklist"
        assert checklist.value == test_value
        assert checklist.title is None
        assert checklist.actions == []

    @pytest.mark.parametrize(
        "test_value, options",
        [
            ([5], ["A", "B", "C"]),
            ([5], [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}]),
            (["D"], ["A", "B", "C"]),
            (["D"], [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}]),
            ([True], ["A", "B", "C"]),
            ([True], [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}]),
        ],
    )
    def test_create_checklist_invalid_value_non_existing(self, test_value, options):
        with pytest.raises(ValidationError, match="Please provide a valid value from `options`."):
            Checklist(value=test_value, options=options)

    def test_create_checklist_invalid_value_format(self):
        with pytest.raises(ValidationError, match="value is not a valid list"):
            Checklist(value="A", options=["A", "B", "C"])

    def test_set_action_via_validator(self, test_action_function):
        checklist = Checklist(actions=[Action(function=test_action_function)])
        actions_chain = checklist.actions[0]
        assert actions_chain.trigger.component_property == "value"


class TestChecklistBuild:
    """Tests model build method."""

    def test_checklist_build(self, expected_checklist):
        checklist = Checklist(options=["A", "B", "C"], id="checklist_id", title="Title").build()

        result = json.loads(json.dumps(checklist, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_checklist, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected
