import re

import pytest
from dash import no_update

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
            vm.Button(id="button_1", text="Set Europe"),
            vm.Graph(id="scatter_chart_1", figure=standard_px_chart),
            vm.AgGrid(id="ag_grid_1", figure=standard_ag_grid),
            vm.Table(id="table_1", figure=standard_dash_table),
        ],
        controls=[
            vm.Filter(
                id="filter_page_1",
                targets=["table_1"],
                column="continent",
                selector=vm.Dropdown(multi=True),
            ),
            vm.Filter(
                id="filter_page_1_single_select",
                targets=["table_1"],
                column="continent",
                selector=vm.Dropdown(multi=False),
            ),
            vm.Parameter(
                id="cascade_param_single",
                targets=["scatter_chart_1.x"],
                selector=vm.Cascader(multi=False, options={"K": ["leaf_a", "leaf_b"]}),
            ),
            vm.Parameter(
                id="cascade_param_multi",
                targets=["scatter_chart_1.y"],
                selector=vm.Cascader(multi=True, options={"K": ["leaf_a", "leaf_b", "leaf_c"]}),
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


@pytest.fixture
def managers_page_hierarchical_filter_set_control(standard_px_chart):
    vm.Page(
        id="hier-set-page",
        title="hier",
        components=[
            vm.Button(id="hier_set_btn", text="Set"),
            vm.Graph(id="hier_set_chart", figure=standard_px_chart),
        ],
        controls=[
            vm.Filter(
                id="hier_set_filter",
                targets=["hier_set_chart"],
                column=["continent", "country"],
                selector=vm.Cascader(multi=False),
            ),
        ],
    )
    Vizro._pre_build()


class TestSetControlInstantiation:
    """Tests set control instantiation."""

    def test_create_set_control_mandatory_only(self):
        action = set_control(control="control_id", value="some_value")

        assert action.type == "set_control"
        assert action.control == "control_id"
        assert action.value == "some_value"


@pytest.mark.usefixtures("managers_two_pages_for_set_control")
class TestSetControlPreBuild:
    """Tests set control pre_build method."""

    def test_pre_build_control_model_on_same_page(self):
        # Add action to relevant component and target a control on the same page
        action = set_control(control="filter_page_1", value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action._same_page is True

    def test_pre_build_control_model_on_different_page(self):
        # Add action to relevant component and target a control on different page with show_in_url=True
        action = set_control(control="filter_page_2_show_in_url_true", value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action._same_page is False

    def test_pre_build_parent_model_does_not_support_set_control(self):
        action = set_control(control="filter_page_1", value="Europe")

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
        action = set_control(control="invalid_id", value="Europe")
        model_manager["button_1"].actions = action

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
        action = set_control(control="filter_not_in_page", value="Europe")
        model_manager["button_1"].actions = action

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
        action = set_control(control="scatter_chart_2", value="Europe")
        model_manager["button_1"].actions = action

        with pytest.raises(
            TypeError,
            match=re.escape(
                "Model with ID `scatter_chart_2` used as a `control` in `set_control` action must be a control model "
                "(e.g. Filter, Parameter) whose selector is categorical (Dropdown, Checklist, RadioItems) or "
                "hierarchical (Cascader)."
            ),
        ):
            action.pre_build()

    @pytest.mark.parametrize(
        "selector",
        [vm.Slider, vm.RangeSlider, vm.DatePicker, vm.Switch],
    )
    def test_pre_build_control_selector_is_not_categorical(self, selector):
        # Add control with non-categorical selector to test-page-1
        model_manager["test-page-1"].controls.append(
            vm.Filter(id="non_categorical", column="continent", selector=selector())
        )

        # Add action to relevant component and target a non-categorical control
        action = set_control(control="non_categorical", value="Europe")
        model_manager["button_1"].actions = action

        with pytest.raises(
            TypeError,
            match=re.escape(
                "Model with ID `non_categorical` used as a `control` in `set_control` action must be a control model "
                "(e.g. Filter, Parameter) whose selector is categorical (Dropdown, Checklist, RadioItems) or "
                "hierarchical (Cascader)."
            ),
        ):
            action.pre_build()

    def test_pre_build_control_model_on_different_page_show_in_url_false(self):
        # Add action to relevant component and target a control on different page with show_in_url=False
        action = set_control(control="filter_page_2_show_in_url_false", value="Europe")
        model_manager["button_1"].actions = action

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

    def test_function_trigger_none_resets_control_to_original_value(self):
        # Add action to relevant component and target a control on the same page
        action = set_control(control="filter_page_1", value=None)
        # Any other model that supports set_control can be used here, but the Button used for the simplicity.
        # Button._get_value_from_trigger returns None as set_control attribute value=None
        model_manager["button_1"].actions = action
        # Call pre_build to set _same_page attribute
        action.pre_build()

        # Mock original value in controls store
        original_value = ["Asia", "Europe"]
        controls_store = {
            "filter_page_1": {
                "originalValue": original_value,
            }
        }

        # Call function method with a mock trigger value of None
        result = action.function(_trigger=None, _controls_store=controls_store)
        expected = original_value

        assert result == expected

    @pytest.mark.parametrize("same_page, expected", [(True, no_update), (False, (no_update, no_update))])
    def test_function_trigger_returns_no_update(self, same_page, expected):
        # Add action to an AgGrid as the AgGrid returns no_update if set_control value is a key from the
        # CELL_CLICKED_MAPPING (e.g. "column"), and trigger does not contain "cellClicked"
        action = set_control(control="filter_page_1", value="column")
        model_manager["ag_grid_1"].actions = action

        # Set _same_page as the output depends on it.
        action._same_page = same_page

        # Call function method with a mock trigger value of None
        result = action.function(_trigger={"selectedRows": []}, _controls_store={})

        assert result == expected

    @pytest.mark.parametrize(
        "control, value, expected_result",
        [
            # Single-select control
            ("filter_page_1_single_select", [], no_update),
            ("filter_page_1_single_select", "Europe", "Europe"),
            ("filter_page_1_single_select", ["Europe"], "Europe"),
            ("filter_page_1_single_select", ["Asia", "Europe"], no_update),
            # Multi-select control
            ("filter_page_1", [], []),
            ("filter_page_1", "Europe", ["Europe"]),
            ("filter_page_1", ["Europe"], ["Europe"]),
            ("filter_page_1", ["Asia", "Europe"], ["Asia", "Europe"]),
            # Hierarchical single-select
            ("cascade_param_single", [], no_update),
            ("cascade_param_single", "leaf_a", "leaf_a"),
            ("cascade_param_single", ["leaf_b"], "leaf_b"),
            ("cascade_param_single", ["leaf_a", "leaf_b"], no_update),
            # Hierarchical multi-select
            ("cascade_param_multi", [], []),
            ("cascade_param_multi", "leaf_a", ["leaf_a"]),
            ("cascade_param_multi", ["leaf_b", "leaf_c"], ["leaf_b", "leaf_c"]),
        ],
    )
    def test_function_different_value_for_different_controls(self, control, value, expected_result):
        # Add action to relevant component and target a control on the same page
        action = set_control(control=control, value=value)
        # Any other model that supports set_control can be used here, but the Button used for the simplicity.
        # Button._get_value_from_trigger returns value as set_control attribute value=value
        model_manager["button_1"].actions = action
        # Call pre_build to set _same_page attribute
        action.pre_build()

        # Call function method with a mock trigger value
        result = action.function(_trigger=None, _controls_store={})

        assert result == expected_result

    def test_function_control_model_on_same_page(self):
        # Add action to relevant component and target a control on the same page
        action = set_control(control="filter_page_1", value="Europe")
        # Any other model that supports set_control can be used here, but the Button used for the simplicity.
        # Button._get_value_from_trigger returns "Europe" as set_control attribute value="Europe"
        model_manager["button_1"].actions = action
        # Call pre_build to set _same_page attribute
        action.pre_build()

        # Call function method with a mock trigger value
        result = action.function(_trigger=None, _controls_store={})
        expected = ["Europe"]

        assert result == expected

    def test_function_control_model_on_different_page(self, mocker):
        # Add action to relevant component and target a control on different page with show_in_url=True
        action = set_control(control="filter_page_2_show_in_url_true", value="Europe")
        # Any other model that supports set_control can be used here, but the Button used for the simplicity.
        # Button._get_value_from_trigger returns "Europe" as set_control attribute value="Europe"
        model_manager["button_1"].actions = action
        # Call pre_build to set _same_page attribute
        action.pre_build()

        # Mock dash.get_relative_path as it's used in set_control.function
        mocker.patch.object(set_control_module, "get_relative_path", return_value="/mocked_path")

        # Call function method with a mock trigger value
        result_relative_path, result_url_query_params = action.function(_trigger=None, _controls_store={})
        # From mocked get_relative_path
        expected_relative_path = "/mocked_path"
        # Value ["Europe"] base64 encoded is b64_WyJFdXJvcGUiXQ
        expected_url_query_params = "?filter_page_2_show_in_url_true=b64_WyJFdXJvcGUiXQ"

        assert result_relative_path == expected_relative_path
        assert result_url_query_params == expected_url_query_params


@pytest.mark.usefixtures("managers_two_pages_for_set_control")
class TestSetControlOutputs:
    """Tests set control outputs."""

    def test_outputs_control_model_on_same_page(self):
        # Add action to relevant component and target a control on the same page
        action = set_control(control="filter_page_1", value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action.outputs == "filter_page_1"

    def test_outputs_control_model_on_different_page(self):
        # Add action to relevant component and target a control on different page with show_in_url=True
        action = set_control(control="filter_page_2_show_in_url_true", value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action.outputs == ["vizro_url.pathname", "vizro_url.search"]


@pytest.mark.usefixtures("managers_page_hierarchical_filter_set_control")
class TestSetControlHierarchicalFilter:
    def test_pre_build_same_page(self):
        action = set_control(control="hier_set_filter", value="Germany")
        model_manager["hier_set_btn"].actions = action
        action.pre_build()
        assert action._same_page is True
