import re

import numpy as np
import pytest
from asserts import assert_component_equal
from dash import html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm
from vizro.models._models_utils import (
    _assign_component_grid_area,
    _create_component_container,
    get_unique_grid_component_ids,
)


@pytest.fixture(params=[vm.Container, vm.Page])
def model(request):
    return request.param


class TestSharedValidators:
    def test_set_components_validator(self, model):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            model(title="Title", components=[])

    def test_set_layout_valid(self, model):
        model(title="Title", components=[vm.Button(), vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    def test_set_layout_invalid(self, model):
        with pytest.raises(ValidationError, match="Number of page and grid components need to be the same."):
            model(title="Title", components=[vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    def test_check_for_valid_component_types(self, model):
        with pytest.raises(
            ValidationError, match=re.escape("(allowed values: 'button', 'card', 'container', 'graph', 'table')")
        ):
            model(title="Page Title", components=[vm.Checklist()])


class TestSharedLayoutFunctions:
    @pytest.mark.parametrize("grid", [[[0, -1], [1, 2]], [[0, -1, 1, 2]], [[-1, -1, -1], [0, 1, 2]]])
    def test_get_unique_grid_component_ids(self, grid):
        result = get_unique_grid_component_ids(grid)
        expected = np.array([0, 1, 2])

        assert isinstance(result, np.ndarray)
        assert (result == expected).all()

    def test_assign_component_grid_area_default(self, model):
        model = model(title="Title", components=[vm.Button(), vm.Button()])
        result = _assign_component_grid_area(model)
        assert_component_equal(
            result,
            [
                html.Div(style={"gridColumn": "1/2", "gridRow": "1/2"}),
                html.Div(style={"gridColumn": "1/2", "gridRow": "2/3"}),
            ],
            keys_to_strip={"children"},
        )

    def test_assign_component_grid_area_with_layout(self, model):
        model = model(title="Title", components=[vm.Button(), vm.Button()], layout=vm.Layout(grid=[[0, 1]]))
        result = _assign_component_grid_area(model)
        assert_component_equal(
            result,
            [
                html.Div(style={"gridColumn": "1/2", "gridRow": "1/2"}),
                html.Div(style={"gridColumn": "2/3", "gridRow": "1/2"}),
            ],
            keys_to_strip={"children"},
        )

    def test_create_component_container(self, model):
        model = model(title="Title", components=[vm.Button(), vm.Button()])
        result = _create_component_container(model, [html.Div(), html.Div()])
        assert_component_equal(
            result,
            html.Div(
                className="grid-layout",
                style={
                    "gridRowGap": "12px",
                    "gridColumnGap": "12px",
                    "gridTemplateColumns": "repeat(1,minmax(0px, 1fr))",
                    "gridTemplateRows": "repeat(2,minmax(0px, 1fr))",
                },
            ),
            keys_to_strip={"children"},
        )
