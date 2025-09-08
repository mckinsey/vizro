import re

import pytest

import vizro.models as vm
from vizro import Vizro
from vizro.actions import set_control
from vizro.managers import model_manager


@pytest.fixture
def managers_two_pages_for_set_control(standard_px_chart, standard_ag_grid):
    """Instantiates the model_manager and the data_manager with two pages."""
    vm.Page(
        id="test-page-1",
        title="test-page-1",
        components=[
            vm.Graph(id="scatter_chart_1", figure=standard_px_chart),
            vm.Button(id="button_1"),
        ],
        controls=[
            vm.Filter(
                id="filter_page_1",
                column="continent",
            ),
        ],
    )

    vm.Page(
        id="test-page-2",
        title="test-page-2",
        components=[
            vm.Graph(id="scatter_chart_2", figure=standard_px_chart),
        ],
        controls=[
            vm.Filter(
                id="filter_page_2_show_in_url_false",
                column="continent",
            ),
            vm.Filter(
                id="filter_page_2_show_in_url_true",
                column="continent",
                show_in_url=True,
            ),
        ],
    )

    Vizro._pre_build()


@pytest.mark.usefixtures("managers_two_pages_for_set_control")
@pytest.mark.filterwarnings("ignore:.*experimental.*:FutureWarning")
class TestSetControlPreBuild:
    """Tests set control pre_build method."""

    def test_pre_build_target_model_on_same_page(self):
        # Add action to relevant component and set target to a control on the same page
        action = set_control(target="filter_page_1", value="continent")
        model_manager["scatter_chart_1"].actions = action

        action.pre_build()

        assert action._same_page is True

    def test_pre_build_target_model_on_different_page(self):
        # Add action to relevant component and set target to a control on different page with show_in_url=True
        action = set_control(target="filter_page_2_show_in_url_true", value="continent")
        model_manager["scatter_chart_1"].actions = action

        action.pre_build()

        assert action._same_page is False

    def test_pre_build_parent_model_does_not_support_set_control(self):
        action = set_control(target="filter_page_1", value="continent")

        # Add action to the component that does not support set_control
        model_manager["button_1"].actions = action

        with pytest.raises(
            ValueError,
            match=re.escape(
                "`set_control` action was added to the model with ID `button_1`, but this action can only be used with"
                " models that support it (e.g. Graph, AgGrid)."
            ),
        ):
            action.pre_build()

    def test_pre_build_target_model_does_not_exist_in_model_manager(self):
        # Add action to relevant component and set invalid target
        action = set_control(target="invalid_id", value="continent")
        model_manager["scatter_chart_1"].actions = action

        with pytest.raises(
            ValueError,
            match=re.escape(
                "Model with ID `invalid_id` used as a `target` in `set_control` action not found in the dashboard. "
                "Please provide a valid control ID that exists in the dashboard."
            ),
        ):
            action.pre_build()

    def test_pre_build_target_model_exists_in_model_manager_but_not_in_any_page(self):
        # Add a model to model_manager that is not part of any page
        vm.Filter(id="filter_not_in_page", column="continent")

        # Add action to relevant component and set target to the model not in any page
        action = set_control(target="filter_not_in_page", value="continent")
        model_manager["scatter_chart_1"].actions = action

        with pytest.raises(
            ValueError,
            match=re.escape(
                "Model with ID `filter_not_in_page` used as a `target` in `set_control` action not found in the "
                "dashboard. Please provide a valid control ID that exists in the dashboard."
            ),
        ):
            action.pre_build()

    def test_pre_build_target_model_is_not_control(self):
        # Add action to relevant component and set target to a Graph (non-control) model
        action = set_control(target="scatter_chart_2", value="continent")
        model_manager["scatter_chart_1"].actions = action

        with pytest.raises(
            TypeError,
            match=re.escape(
                "Model with ID `scatter_chart_2` used as a `target` in `set_control` action must be a control model "
                "(e.g. Filter, Parameter) that uses a categorical selector (e.g. Dropdown, Checklist or RadioItems)."
            ),
        ):
            action.pre_build()

    @pytest.mark.parametrize(
        "selector",
        [vm.Slider, vm.RangeSlider, vm.DatePicker, vm.Switch],
    )
    def test_pre_build_target_model_is_control_but_selector_not_categorical(self, selector):
        # Add control with non-categorical selector to test-page-1
        model_manager["test-page-1"].controls.append(
            vm.Filter(id="non_categorical", column="continent", selector=selector())
        )

        # Add action to relevant component and set target to the non-categorical control
        action = set_control(target="non_categorical", value="continent")
        model_manager["scatter_chart_1"].actions = action

        with pytest.raises(
            TypeError,
            match=re.escape(
                "Model with ID `non_categorical` used as a `target` in `set_control` action must be a control model "
                "(e.g. Filter, Parameter) that uses a categorical selector (e.g. Dropdown, Checklist or RadioItems)."
            ),
        ):
            action.pre_build()

    def test_pre_build_target_model_on_different_page_show_in_url_false(self):
        # Add action to relevant component and set target to a control on different page with show_in_url=False
        action = set_control(target="filter_page_2_show_in_url_false", value="continent")
        model_manager["scatter_chart_1"].actions = action

        with pytest.raises(
            ValueError,
            match=re.escape(
                "Model with ID `filter_page_2_show_in_url_false` used as a `target` in `set_control` action is on a "
                "different page from the trigger and so must have `show_in_url=True`."
            ),
        ):
            action.pre_build()


@pytest.mark.usefixtures("managers_two_pages_for_set_control")
@pytest.mark.filterwarnings("ignore:.*experimental.*:FutureWarning")
class TestSetControlOutputs:
    """Tests set control outputs."""

    def test_outputs_target_model_on_same_page(self):
        # Add action to relevant component and set target to a control on the same page
        action = set_control(target="filter_page_1", value="continent")
        model_manager["scatter_chart_1"].actions = action

        action.pre_build()

        assert action.outputs == "filter_page_1"

    def test_outputs_target_model_on_different_page(self):
        # Add action to relevant component and set target to a control on different page with show_in_url=True
        action = set_control(target="filter_page_2_show_in_url_true", value="continent")
        model_manager["scatter_chart_1"].actions = action

        action.pre_build()

        assert action.outputs == ["vizro_url.pathname", "vizro_url.search"]


# TODO PP: Add tests
class TestSetControlFunction:
    """Tests set control function."""
