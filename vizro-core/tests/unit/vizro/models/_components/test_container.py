"""Unit tests for vizro.models.Container."""
import re

import pytest

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm


class TestContainerInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_container_mandatory_only(self):
        container = vm.Container(title="Title", components=[vm.Button(), vm.Button()])
        assert isinstance(container.components[0], vm.Button) and isinstance(container.components[1], vm.Button)
        assert container.layout.grid == [[0], [1]]
        assert container.title == "Title"

    def test_create_container_mandatory_and_optional(self):
        container = vm.Container(
            title="Title",
            components=[vm.Button(), vm.Button()],
            id="my-id",
            layout=vm.Layout(grid=[[0, 1]]),
        )
        assert isinstance(container.components[0], vm.Button) and isinstance(container.components[1], vm.Button)
        assert container.layout.grid == [[0, 1]]
        assert container.title == "Title"
        assert container.id == "my-id"

    def test_mandatory_title_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Container(components=[vm.Button()])

    def test_mandatory_components_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Container(title="Title")

    def test_mandatory_components_invalid(self):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.Container(title="Title", components=[])

    def test_set_layout_valid(self):
        vm.Container(title="Title", components=[vm.Button(), vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    def test_set_layout_invalid(self):
        with pytest.raises(ValidationError, match="Number of page and grid components need to be the same."):
            vm.Container(title="Title", components=[vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    def test_valid_component_types(self, standard_px_chart, standard_dash_table):
        vm.Container(
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
    def test_invalid_component_types(self, test_component):
        with pytest.raises(
            ValidationError,
            match=re.escape("(allowed values: 'button', 'card', 'graph', 'table', 'container')"),
        ):
            vm.Container(title="Page Title", components=[test_component])
