import pytest
from asserts import assert_component_equal
from dash import html
from pydantic import ValidationError

import vizro.models as vm
from vizro._constants import GAP_DEFAULT


class TestFlexInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_flex_mandatory_only(self):
        flex = vm.Flex()
        assert hasattr(flex, "id")
        assert flex.direction == "column"
        assert flex.gap == GAP_DEFAULT
        assert flex.wrap is False

    @pytest.mark.parametrize("test_unit", ["0px", "4px", "4rem", "4em", "4%"])
    def test_create_flex_mandatory_and_optional(self, test_unit):
        flex = vm.Flex(direction="row", gap=test_unit, wrap=True)

        assert hasattr(flex, "id")
        assert flex.direction == "row"
        assert flex.gap == test_unit
        assert flex.wrap is True

    @pytest.mark.parametrize("test_unit", ["0", "calc(100% - 3px)", "4ex", "4ch", "4vh", "4vw", "4vmin", "4vmax"])
    def test_invalid_unit_size(self, test_unit):
        with pytest.raises(ValidationError, match="1 validation error for Flex"):
            vm.Flex(gap=test_unit)


class TestFlexBuild:
    def test_flex_build_default(self):
        result = vm.Flex(id="flex").build()
        expected = html.Div(
            [],
            style={"gap": GAP_DEFAULT},
            className="d-flex flex-column flex-nowrap",
            id="flex",
        )
        assert_component_equal(result, expected)

    def test_flex_build_optional(self):
        result = vm.Flex(id="flex", direction="row", gap="40px", wrap=True).build()
        expected = html.Div(
            [],
            style={"gap": "40px"},
            className="d-flex flex-row flex-wrap",
            id="flex",
        )
        assert_component_equal(result, expected)
