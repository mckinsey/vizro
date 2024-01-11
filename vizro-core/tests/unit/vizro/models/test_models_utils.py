import re

import pytest

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm


@pytest.mark.parametrize("Model", [vm.Container, vm.Page])
class TestReusedValidators:
    def test_set_components_validator(self, Model):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            Model(title="Title", components=[])

    def test_set_layout_valid(self, Model):
        Model(title="Title", components=[vm.Button(), vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    def test_set_layout_invalid(self, Model):
        with pytest.raises(ValidationError, match="Number of page and grid components need to be the same."):
            Model(title="Title", components=[vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    def test_valid_component_types(self, standard_px_chart, standard_dash_table, Model):
        Model(
            title="Title",
            components=[
                vm.Graph(figure=standard_px_chart),
                vm.Card(text="""# Header 1"""),
                vm.Button(),
                vm.Table(figure=standard_dash_table),
                vm.Container(title="Title", components=[vm.Button()]),
            ],
        )

    @pytest.mark.parametrize(
        "test_component",
        [vm.Checklist(), vm.Dropdown(), vm.RadioItems(), vm.RangeSlider(), vm.Slider()],
    )
    def test_invalid_component_types(self, test_component, Model):
        with pytest.raises(
            ValidationError,
            match=re.escape("(allowed values: 'button', 'card', 'graph', 'table', 'container')"),
        ):
            Model(title="Title", components=[test_component])
