import pytest
import vizro.models as vm
from vizro_ai.dashboard._pydantic_output import _get_pydantic_output
from vizro_ai.dashboard.response_models.layout import LayoutPlan

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError


# class TestLayoutProxyModel:
#     """Test layout proxy creation"""
#
#     def test_create_layout_proxy_model_invalid_rows(self, grid_invalid_rows):
#         with pytest.raises(ValidationError, match="All rows must be of same length"):
#             LayoutProxyModel(grid=grid_invalid_rows)
#
#     def test_create_layout_proxy_model_invalid_values(self, grid_invalid_values):
#         with pytest.raises(ValidationError, match="Grid must contain consecutive integers starting from 0."):
#             LayoutProxyModel(grid=grid_invalid_values)


class TestLayoutPlan:
    """Test layout creation"""

    def test_structured_output_layout_create(self, fake_llm_layout, layout_description):
        structured_output = _get_pydantic_output(
            query=layout_description, llm_model=fake_llm_layout, response_model=vm.Layout, df_info=None
        )
        assert structured_output.dict(exclude={"id": True}) == vm.Layout(grid=[[0, 1]]).dict(exclude={"id": True})

    def test_layout_plan(self):
        layout_plan = LayoutPlan(
            layout_description="Create a layout with a graph on the left and a card on the right.",
            layout_grid_template_areas=["graph card"],
        )
        layout = layout_plan.create(["graph", "card"])

        assert layout.dict(exclude={"id": True}) == vm.Layout(grid=[[0, 1]]).dict(exclude={"id": True})

    def test_layout_plan_no_description(self, fake_llm_layout):
        layout_plan = LayoutPlan(
            layout_description="N/A",
            layout_grid_template_areas=["graph card"],
        )
        layout = layout_plan.create(fake_llm_layout)

        assert layout is None
