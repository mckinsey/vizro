"""Unit tests for the set_controls action and the deprecated set_control alias.

End-to-end behavior (pre_build validation, callback function, cross-page sync, drill-through) is exercised through the
deprecated `set_control` alias in test_legacy_set_control.py, which delegates to the same set_controls implementation,
and through the Filter/Parameter default-action tests. These tests focus on the canonical set_controls API surface.
"""

import pytest
from pydantic import ValidationError

import vizro.actions as va


class TestSetControlsInstantiation:
    def test_defaults(self):
        action = va.set_controls(controls=["filter_1"])
        assert action.type == "set_controls"
        assert action.controls == ["filter_1"]
        assert action.value is None

    def test_multiple_controls_and_value(self):
        action = va.set_controls(controls=["filter_1", "filter_2"], value="species")
        assert action.controls == ["filter_1", "filter_2"]
        assert action.value == "species"

    def test_controls_must_be_a_list(self):
        # A single id string is not accepted; controls must be a list of ids.
        with pytest.raises(ValidationError):
            va.set_controls(controls="filter_1")

    def test_control_ids_dedupe_preserves_order(self):
        assert va.set_controls(controls=["a", "a", "b", "a"])._control_ids == ["a", "b"]


class TestSetControlDeprecatedAlias:
    def test_set_control_is_subclass_of_set_controls(self):
        assert issubclass(va.set_control, va.set_controls)

    def test_set_control_emits_deprecation_warning(self):
        with pytest.warns(FutureWarning, match="`set_control` is deprecated"):
            va.set_control(control="filter_1")

    @pytest.mark.filterwarnings("ignore:`set_control` is deprecated:FutureWarning")
    def test_single_control_maps_to_controls_list(self):
        action = va.set_control(control="filter_1")
        assert action.type == "set_control"
        assert action.controls == ["filter_1"]

    @pytest.mark.filterwarnings("ignore:`set_control` is deprecated:FutureWarning")
    def test_list_control_maps_to_controls(self):
        action = va.set_control(control=["filter_1", "filter_2"])
        assert action.controls == ["filter_1", "filter_2"]
