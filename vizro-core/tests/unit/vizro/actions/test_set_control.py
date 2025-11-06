import re

import pytest

import vizro.actions._set_control as set_control_module
import vizro.models as vm
from vizro import Vizro
from vizro.actions import set_control
from vizro.managers import model_manager


@pytest.fixture
def managers_two_pages_for_set_control(standard_px_chart, standard_ag_grid, standard_dash_table):
    """Instantiates the model_manager and the data_manager with two pages."""
    vm.Page(
        id="test-page-1",
        title="test-page-1",
        components=[
            vm.Graph(id="scatter_chart_1", figure=standard_px_chart),
            vm.Table(id="table_1", figure=standard_dash_table),
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


class TestSetControlInstantiation:
    """Tests set control instantiation."""

    def test_create_set_control_mandatory_only(self):
        action = set_control(control="control_id", value="value")

        assert action.type == "set_control"
        assert action.control == "control_id"
        assert action.value == "value"


@pytest.mark.usefixtures("managers_two_pages_for_set_control")
class TestSetControlPreBuild:
    """Tests set control pre_build method."""

    def test_pre_build_control_model_on_same_page(self):
        # Add action to relevant component and target a control on the same page
        action = set_control(control="filter_page_1", value="continent")
        model_manager["scatter_chart_1"].actions = action

        action.pre_build()

        assert action._same_page is True

    def test_pre_build_control_model_on_different_page(self):
        # Add action to relevant component and target a control on different page with show_in_url=True
        action = set_control(control="filter_page_2_show_in_url_true", value="continent")
        model_manager["scatter_chart_1"].actions = action

        action.pre_build()

        assert action._same_page is False

    def test_pre_build_parent_model_does_not_support_set_control(self):
        action = set_control(control="filter_page_1", value="continent")

        # Add action to the component that does not support set_control
        model_manager["table_1"].actions = action

        with pytest.raises(
            ValueError,
            match=re.escape(
                "`set_control` action was added to the model with ID `table_1`, "
                "but this action can only be used with models that support it (e.g. Graph, AgGrid, Figure etc). "
                "See all models that can source a `set_control` at "
                "https://vizro.readthedocs.io/en/stable/pages/API-reference/actions/#vizro.actions.set_control"
            ),
        ):
            action.pre_build()

    def test_pre_build_control_model_does_not_exist_in_model_manager(self):
        # Add action to relevant component and set invalid control
        action = set_control(control="invalid_id", value="continent")
        model_manager["scatter_chart_1"].actions = action

        with pytest.raises(
            ValueError,
            match=re.escape(
                "Model with ID `invalid_id` used as a `control` in `set_control` action not found in the dashboard. "
                "Please provide a valid control ID that exists in the dashboard."
            ),
        ):
            action.pre_build()

    def test_pre_build_control_model_exists_in_model_manager_but_not_in_any_page(self):
        # Add a model to model_manager that is not part of any page
        vm.Filter(id="filter_not_in_page", column="continent")

        # Add action to relevant component and set control to the model not in any page
        action = set_control(control="filter_not_in_page", value="continent")
        model_manager["scatter_chart_1"].actions = action

        with pytest.raises(
            ValueError,
            match=re.escape(
                "Model with ID `filter_not_in_page` used as a `control` in `set_control` action not found in the "
                "dashboard. Please provide a valid control ID that exists in the dashboard."
            ),
        ):
            action.pre_build()

    def test_pre_build_control_model_is_not_control(self):
        # Add action to relevant component and target a Graph (non-control) model
        action = set_control(control="scatter_chart_2", value="continent")
        model_manager["scatter_chart_1"].actions = action

        with pytest.raises(
            TypeError,
            match=re.escape(
                "Model with ID `scatter_chart_2` used as a `control` in `set_control` action must be a control model "
                "(e.g. Filter, Parameter) that uses a categorical selector (e.g. Dropdown, Checklist or RadioItems)."
            ),
        ):
            action.pre_build()

    @pytest.mark.parametrize(
        "selector",
        [vm.Slider, vm.RangeSlider, vm.DatePicker, vm.Switch],
    )
    def test_pre_build_control_model_is_control_but_selector_not_categorical(self, selector):
        # Add control with non-categorical selector to test-page-1
        model_manager["test-page-1"].controls.append(
            vm.Filter(id="non_categorical", column="continent", selector=selector())
        )

        # Add action to relevant component and target a non-categorical control
        action = set_control(control="non_categorical", value="continent")
        model_manager["scatter_chart_1"].actions = action

        with pytest.raises(
            TypeError,
            match=re.escape(
                "Model with ID `non_categorical` used as a `control` in `set_control` action must be a control model "
                "(e.g. Filter, Parameter) that uses a categorical selector (e.g. Dropdown, Checklist or RadioItems)."
            ),
        ):
            action.pre_build()

    def test_pre_build_control_model_on_different_page_show_in_url_false(self):
        # Add action to relevant component and target a control on different page with show_in_url=False
        action = set_control(control="filter_page_2_show_in_url_false", value="continent")
        model_manager["scatter_chart_1"].actions = action

        with pytest.raises(
            ValueError,
            match=re.escape(
                "Model with ID `filter_page_2_show_in_url_false` used as a `control` in `set_control` action is on a "
                "different page from the trigger and so must have `show_in_url=True`."
            ),
        ):
            action.pre_build()


@pytest.mark.usefixtures("managers_two_pages_for_set_control")
class TestSetControlFunction:
    """Tests set control function."""

    def test_function_control_model_on_same_page(self):
        # Add action to relevant component and target a control on the same page
        action = set_control(control="filter_page_1", value="continent")
        # Any other model that supports set_control can be used here, but the Graph used for the simplicity.
        model_manager["scatter_chart_1"].actions = action
        # Call pre_build to set _same_page attribute
        action.pre_build()

        # Call function method with a mock trigger value
        result = action.function(_trigger={"points": [{"customdata": ["Europe"]}]})
        expected = "Europe"

        assert result == expected

    def test_function_control_model_on_different_page(self, mocker):
        # Add action to relevant component and target a control on different page with show_in_url=True
        action = set_control(control="filter_page_2_show_in_url_true", value="continent")
        # Any other model that supports set_control can be used here, but the Graph used for the simplicity.
        model_manager["scatter_chart_1"].actions = action
        # Call pre_build to set _same_page attribute
        action.pre_build()

        # Mock dash.get_relative_path as it's used in set_control.function
        mocker.patch.object(set_control_module, "get_relative_path", return_value="/mocked_path")

        # Call function method with a mock trigger value
        result_relative_path, result_url_query_params = action.function(
            _trigger={"points": [{"customdata": ["Europe"]}]},
        )
        # From mocked get_relative_path
        expected_relative_path = "/mocked_path"
        # Value "Europe" base64 encoded is b64_IkV1cm9wZSI
        expected_url_query_params = "?filter_page_2_show_in_url_true=b64_IkV1cm9wZSI"

        assert result_relative_path == expected_relative_path
        assert result_url_query_params == expected_url_query_params


@pytest.mark.usefixtures("managers_two_pages_for_set_control")
class TestSetControlOutputs:
    """Tests set control outputs."""

    def test_outputs_control_model_on_same_page(self):
        # Add action to relevant component and target a control on the same page
        action = set_control(control="filter_page_1", value="continent")
        model_manager["scatter_chart_1"].actions = action

        action.pre_build()

        assert action.outputs == "filter_page_1"

    def test_outputs_control_model_on_different_page(self):
        # Add action to relevant component and target a control on different page with show_in_url=True
        action = set_control(control="filter_page_2_show_in_url_true", value="continent")
        model_manager["scatter_chart_1"].actions = action

        action.pre_build()

        assert action.outputs == ["vizro_url.pathname", "vizro_url.search"]
