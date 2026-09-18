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
            vm.Filter(
                id="filter_page_1_slider",
                targets=["table_1"],
                column="lifeExp",
                selector=vm.Slider(),
            ),
            vm.Filter(
                id="filter_page_1_range_slider",
                targets=["table_1"],
                column="lifeExp",
                selector=vm.RangeSlider(),
            ),
            vm.Filter(
                id="filter_page_1_boolean",
                targets=["table_1"],
                column="is_europe",
                selector=vm.Switch(),
            ),
            vm.Filter(
                id="filter_page_1_date_picker",
                targets=["table_1"],
                column="year",
                selector=vm.DatePicker(range=False),
            ),
            vm.Filter(
                id="filter_page_1_date_picker_range",
                targets=["table_1"],
                column="year",
                selector=vm.DatePicker(),
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
def managers_three_pages_for_set_control(standard_px_chart):
    """A source page plus two separate target pages, for multi-page drill-through tests."""
    vm.Page(
        id="src-page",
        title="src-page",
        components=[
            vm.Button(id="src_button", text="Set"),
            vm.Graph(id="src_graph", figure=standard_px_chart),
        ],
        controls=[vm.Filter(id="src_filter", column="continent")],
    )
    vm.Page(
        id="target-page-a",
        title="target-page-a",
        components=[vm.Graph(id="graph_a", figure=standard_px_chart)],
        controls=[vm.Filter(id="filter_a", column="continent")],
    )
    vm.Page(
        id="target-page-b",
        title="target-page-b",
        components=[vm.Graph(id="graph_b", figure=standard_px_chart)],
        controls=[vm.Filter(id="filter_b", column="continent")],
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


@pytest.fixture
def managers_page_hierarchical_filter_set_control_path(standard_px_chart):
    vm.Page(
        id="hier-set-page-path",
        title="hier-path",
        components=[
            vm.Button(id="hier_set_btn_path", text="Set"),
            vm.Graph(id="hier_set_chart_path", figure=standard_px_chart),
        ],
        controls=[
            vm.Filter(
                id="hier_set_filter_path",
                targets=["hier_set_chart_path"],
                column=["continent", "country"],
                selector=vm.Cascader(multi=False, full_path=True),
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

    def test_create_set_control_with_list_control(self):
        # `control` accepts a list of ids to target several controls at once; the value is preserved as given.
        action = set_control(control=["control_a", "control_b"], value="some_value")

        assert action.type == "set_control"
        assert action.control == ["control_a", "control_b"]
        assert action.value == "some_value"

    def test_notifications_single_set_for_multiple_controls(self):
        # A multi-target set_control is one callback, so it shows a single confirmation - one success/error
        # notification, not one per control.
        action = set_control(control=["control_a", "control_b"], value="some_value")

        assert set(action.notifications) == {"success", "error"}
        assert action.notifications["success"].text == "Controls updated."


class TestNormalizeRangeValue:
    """Tests the range-value shaping helper directly, for both source kinds (`reorder` True/False)."""

    @pytest.mark.parametrize(
        "value, reorder, expected",
        [
            # Non-list scalar -> duplicated into a degenerate [v, v] range (independent of reorder).
            (5, True, [5, 5]),
            (5, False, [5, 5]),
            ("1992-01-01", False, ["1992-01-01", "1992-01-01"]),
            # A scalar empty value (None or "") is a cleared/incomplete selection and is never synced.
            (None, True, None),
            (None, False, None),
            ("", False, None),
            # Empty / incomplete selections are never synced.
            ([], True, None),
            ([1, None], True, None),
            (["1992-01-01", ""], False, None),
            # Single-element list -> degenerate [v, v] range.
            ([1], True, [1, 1]),
            (["1992-01-01"], False, ["1992-01-01", "1992-01-01"]),
            # Selection-order source (reorder=True): two ends sorted into [min, max].
            ([2, 1], True, [1, 2]),
            (["1993-01-01", "1992-01-01"], True, ["1992-01-01", "1993-01-01"]),
            # Important: This is incorrect, so we deliberately send reorder=False for such a case.
            (["2024-01-01T06:00", "2024-01-01"], True, ["2024-01-01", "2024-01-01T06:00"]),
            # Range-selector source (reorder=False): authoritative [start, end] kept as-is...
            ([2, 1], False, [2, 1]),
            (["1993-01-01", "1992-01-01"], False, ["1993-01-01", "1992-01-01"]),
            (["2024-01-01T06:00", "2024-01-01"], False, ["2024-01-01T06:00", "2024-01-01"]),
            # More than two values always collapse to the spanning [min, max], for either source kind.
            ([1, 2, 3, 4], False, [1, 4]),
            ([1, 2, 3, 4], True, [1, 4]),
            (["1992-01-01", "1994-01-01", "1993-01-01"], False, ["1992-01-01", "1994-01-01"]),
        ],
    )
    def test_normalize_range_value(self, value, reorder, expected):
        assert set_control._normalize_range_value(value, reorder=reorder) == expected


@pytest.mark.usefixtures("managers_two_pages_for_set_control")
class TestSetControlPreBuild:
    """Tests set control pre_build method."""

    def test_pre_build_control_model_on_same_page(self):
        # Add action to relevant component and target a control on the same page
        action = set_control(control="filter_page_1", value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action._same_page_controls == ["filter_page_1"]
        assert action._cross_page_controls == []
        # No cross-page target, so there is nothing to navigate to.
        assert action._drill_through_path is None

    def test_pre_build_control_model_on_different_page(self):
        # Target a control on a different page. The trigger (Button) is not a control selector, so this is a
        # drill-through: it navigates to the target's page (see the function/outputs tests).
        action = set_control(control="filter_page_2_show_in_url_true", value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action._same_page_controls == []
        assert action._cross_page_controls == ["filter_page_2_show_in_url_true"]
        assert action._is_drill_through is True
        # A single cross-page target resolves to one unambiguous page to navigate to.
        assert action._drill_through_path == model_manager["test-page-2"].path

    def test_pre_build_multiple_controls_same_page(self):
        # Several same-page targets are all classified as same-page; nothing to navigate to.
        action = set_control(control=["filter_page_1", "filter_page_1_slider"], value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action._same_page_controls == ["filter_page_1", "filter_page_1_slider"]
        assert action._cross_page_controls == []
        assert action._drill_through_path is None

    def test_pre_build_dedupes_repeated_controls(self):
        # A control listed more than once is collapsed (two Outputs to one component in a callback is an error).
        action = set_control(control=["filter_page_1", "filter_page_1"], value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action._control_ids == ["filter_page_1"]
        assert action._same_page_controls == ["filter_page_1"]

    def test_pre_build_mixed_same_and_cross_page(self):
        # A mix of a same-page and a cross-page target: classified into the two lists (order preserved). Even though the
        # single cross-page target resolves to one page, a same-page target means we do NOT navigate (staying to set a
        # control on the current page contradicts leaving it), so no navigation path is set.
        action = set_control(control=["filter_page_1", "filter_page_2_show_in_url_true"], value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action._same_page_controls == ["filter_page_1"]
        assert action._cross_page_controls == ["filter_page_2_show_in_url_true"]
        assert action._drill_through_path is None

    def test_pre_build_invalid_control_in_list_raises(self):
        # Every id in the list is validated; an invalid one raises, naming that id.
        action = set_control(control=["filter_page_1", "invalid_id"], value="Europe")
        model_manager["button_1"].actions = action

        with pytest.raises(
            ValueError,
            match=re.escape(
                "Model with ID `invalid_id` used as a `control` in `set_control` action not found in the dashboard. "
                "Please provide a valid control ID that exists in the dashboard."
            ),
        ):
            action.pre_build()

    def test_pre_build_empty_control_list_raises(self):
        # An empty `control` has nothing to set and would produce zero callback outputs; reject it at build time.
        action = set_control(control=[], value="Europe")
        model_manager["button_1"].actions = action

        with pytest.raises(ValueError, match="has an empty `control`"):
            action.pre_build()

    def test_pre_build_parent_model_does_not_support_set_control(self):
        action = set_control(control="filter_page_1", value="Europe")

        # Add action to the component that does not support set_control
        model_manager["table_1"].actions = action

        with pytest.raises(
            ValueError,
            match=re.escape(
                "`set_control` action was added to the model with ID `table_1`, "
                "but this action can only be used with models that support it "
                "(for example, Graph, AgGrid, Figure, and so on). "
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
                "(for example, Filter, Parameter)."
            ),
        ):
            action.pre_build()

    def test_pre_build_control_model_on_different_page_show_in_url_not_required(self):
        # Cross-page set_control no longer requires the target to have show_in_url=True: the value is carried through
        # the internal controls store, not the URL. pre_build must succeed for a different-page target that has
        # show_in_url=False.
        action = set_control(control="filter_page_2_show_in_url_false", value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action._same_page_controls == []
        assert action._cross_page_controls == ["filter_page_2_show_in_url_false"]
        assert action._is_drill_through is True


@pytest.mark.usefixtures("managers_two_pages_for_set_control")
class TestSetControlFunction:
    """Tests set control function."""

    def test_function_trigger_none_resets_control_to_original_value(self):
        # Add action to relevant component and target a control on the same page
        action = set_control(control="filter_page_1", value=None)
        # Any other model that supports set_control can be used here, but the Button used for the simplicity.
        # Button._get_value_from_trigger returns None as set_control attribute value=None
        model_manager["button_1"].actions = action
        # Call pre_build to classify the target control(s) by page
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

    def test_function_selector_sync_none_clears_multi_target_instead_of_resetting(self):
        # Counterpart to the drill-through reset above: a selector-driven sync (not a drill-through) propagates the
        # source's live value as-is. When the user clears the source selector (value None), the synced multi-select
        # target is cleared to [] - it does NOT fall back to the target's original value.
        action = set_control(control="filter_page_1", value=None)
        model_manager["button_1"].actions = action
        action.pre_build()
        # Simulate a control-selector trigger (a sync mirrors the cleared value rather than resetting).
        action._is_drill_through = False

        # Even with an original value stored, a sync clear must not restore it.
        controls_store = {"filter_page_1": {"originalValue": ["Asia", "Europe"]}}
        result = action.function(_trigger=None, _controls_store=controls_store)

        # filter_page_1 is multi-select, so a cleared value shapes to [] (not the stored ["Asia", "Europe"]).
        assert result == []

    def test_function_selector_sync_none_clears_single_select_target(self):
        # As above but for a single-select target: a cleared sync value stays None (mirrors the empty source) rather
        # than resetting to the target's original value.
        action = set_control(control="filter_page_1_single_select", value=None)
        model_manager["button_1"].actions = action
        action.pre_build()
        action._is_drill_through = False

        controls_store = {"filter_page_1_single_select": {"originalValue": "Asia"}}
        result = action.function(_trigger=None, _controls_store=controls_store)

        assert result is None

    @pytest.mark.parametrize(
        "same_page_controls, cross_page_controls",
        [(["filter_page_1"], []), ([], ["filter_page_1"])],
    )
    def test_function_trigger_returns_no_update(self, same_page_controls, cross_page_controls):
        # Add action to an AgGrid as the AgGrid returns no_update if set_control value is a key from the
        # CELL_CLICKED_MAPPING (e.g. "column"), and trigger does not contain "cellClicked"
        action = set_control(control="filter_page_1", value="column")
        model_manager["ag_grid_1"].actions = action

        # Set the page-classification attributes directly (the output shape depends on them); a no_update trigger must
        # yield no_update regardless of whether the target is on the same page or a different one.
        action._same_page_controls = same_page_controls
        action._cross_page_controls = cross_page_controls

        # Call function method with a mock trigger value of None
        result = action.function(_trigger={"selectedRows": []}, _controls_store={})

        assert result is no_update

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
            # Single-value numerical control
            ("filter_page_1_slider", [], no_update),
            ("filter_page_1_slider", 1, 1),
            ("filter_page_1_slider", [1], 1),
            ("filter_page_1_slider", [1, 2], no_update),
            # Range-value numerical control
            ("filter_page_1_range_slider", [], no_update),
            ("filter_page_1_range_slider", 1, [1, 1]),
            ("filter_page_1_range_slider", [1], [1, 1]),
            # More than two values can only come from a multi-selection source, which has no positional start/end,
            # so they always collapse to the spanning [min, max] regardless of the source kind.
            ("filter_page_1_range_slider", [1, 2, 3, 4], [1, 4]),
            # A two-element value from a non-selection-order source (here a Button) is kept in its given [start, end]
            # slot order. Only AgGrid/Graph selections are reordered by magnitude - see the direct reorder=True cases
            # in test_normalize_range_value and the end-to-end test_function_range_reorders_for_selection_order_source.
            ("filter_page_1_range_slider", [2, 1], [2, 1]),
            # Single-value boolean control
            ("filter_page_1_boolean", [], no_update),
            ("filter_page_1_boolean", True, True),
            ("filter_page_1_boolean", False, False),
            ("filter_page_1_boolean", [True], True),
            ("filter_page_1_boolean", [False], False),
            ("filter_page_1_boolean", [True, False], no_update),
            # Single-value temporal control
            ("filter_page_1_date_picker", [], no_update),
            ("filter_page_1_date_picker", "1992-01-01", "1992-01-01"),
            ("filter_page_1_date_picker", ["1992-01-01"], "1992-01-01"),
            ("filter_page_1_date_picker", ["1992-01-01", "1993-01-01"], no_update),
            # Range temporal control
            ("filter_page_1_date_picker_range", [], no_update),
            ("filter_page_1_date_picker_range", "1992-01-01", ["1992-01-01", "1992-01-01"]),
            ("filter_page_1_date_picker_range", ["1992-01-01"], ["1992-01-01", "1992-01-01"]),
            ("filter_page_1_date_picker_range", ["1992-01-01", "1993-01-01"], ["1992-01-01", "1993-01-01"]),
            (
                "filter_page_1_date_picker_range",
                ["1992-01-01", "1993-01-01", "1994-01-01"],
                ["1992-01-01", "1994-01-01"],
            ),
            # A two-element range value from a non-selection-order source (here a Button) is kept in its given
            # [start, end] slot order (no min/max reorder). This preserves correctness for a range selector whose
            # ends are not lexically ordered - e.g. a DateTimePicker whose start carries a time but whose end is a
            # date-only, whole-day value (["...T06:00", "..."]): reordering would move the start into the end slot.
            # Here a deliberately reversed pair is passed through unchanged.
            ("filter_page_1_date_picker_range", ["1993-01-01", "1992-01-01"], ["1993-01-01", "1992-01-01"]),
            # An incomplete range mid-selection is not synced (returns no_update), instead of crashing on None
            # (a 500 error - the reported DatePicker bug) or dropping the set value into the wrong slot for ""
            # (the reported Time/DateTime picker bug where selecting the start set the target's end).
            ("filter_page_1_date_picker_range", ["1992-01-01", None], no_update),
            ("filter_page_1_date_picker_range", [None, "1993-01-01"], no_update),
            ("filter_page_1_date_picker_range", ["1992-01-01", ""], no_update),
            ("filter_page_1_date_picker_range", ["", "1993-01-01"], no_update),
            # Leaf-mode hierarchical single-select behaves like a flat single-value selector: a bare leaf passes
            # through, and a 1-item list is unwrapped to its single leaf.
            ("cascade_param_single", "leaf_a", "leaf_a"),
            ("cascade_param_single", ["leaf_a"], "leaf_a"),
            # Leaf-mode hierarchical multi-select behaves like a flat multi selector: the list of leaves passes
            # through, and a bare leaf is wrapped into a list.
            ("cascade_param_multi", [], []),
            ("cascade_param_multi", ["leaf_a", "leaf_b"], ["leaf_a", "leaf_b"]),
            ("cascade_param_multi", "leaf_a", ["leaf_a"]),
        ],
    )
    def test_function_different_value_for_different_controls(self, control, value, expected_result):
        # Add action to relevant component and target a control on the same page
        action = set_control(control=control, value=value)
        # Any other model that supports set_control can be used here, but the Button used for the simplicity.
        # Button._get_value_from_trigger returns value as set_control attribute value=value
        model_manager["button_1"].actions = action
        # Call pre_build to classify the target control(s) by page
        action.pre_build()

        # Call function method with a mock trigger value
        result = action.function(_trigger=None, _controls_store={})

        assert result == expected_result

    def test_function_range_reorders_for_selection_order_source(self):
        # An AgGrid emits the selected rows' values in click order, so a reversed 2-row selection reaches a range
        # control inverted. Because the source is a selection-order source (AgGrid), it must be reordered into
        # [min, max] rather than kept in slot order (the DatePicker-range cross-filter regression).
        action = set_control(control="filter_page_1_date_picker_range", value="year")
        model_manager["ag_grid_1"].actions = action
        action.pre_build()

        result = action.function(
            _trigger={"selectedRows": [{"year": "1993-01-01"}, {"year": "1992-01-01"}]},
            _controls_store={},
        )

        assert result == ["1992-01-01", "1993-01-01"]

    def test_function_control_model_on_same_page(self):
        # Add action to relevant component and target a control on the same page
        action = set_control(control="filter_page_1", value="Europe")
        # Any other model that supports set_control can be used here, but the Button used for the simplicity.
        # Button._get_value_from_trigger returns "Europe" as set_control attribute value="Europe"
        model_manager["button_1"].actions = action
        # Call pre_build to classify the target control(s) by page
        action.pre_build()

        # Call function method with a mock trigger value
        result = action.function(_trigger=None, _controls_store={})
        expected = ["Europe"]

        assert result == expected

    def test_function_control_model_on_different_page_drill_through(self, mocker):
        # A figure/component trigger (here a Button) targeting a control on another page is a drill-through: it writes
        # the value into the controls store and navigates to the target control's page.
        action = set_control(control="filter_page_2_show_in_url_true", value="Europe")
        model_manager["button_1"].actions = action
        action.pre_build()
        assert action._is_drill_through is True

        # Mock dash.get_relative_path and dash.set_props as they are used in set_control.function.
        mocker.patch.object(set_control_module, "get_relative_path", return_value="/mocked_path")
        set_props_mock = mocker.patch.object(set_control_module, "set_props")

        controls_store = {"filter_page_2_show_in_url_true": {"currentValue": None}}
        result = action.function(_trigger=None, _controls_store=controls_store)

        # Drill-through navigates: returns the (relative) path of the target control's page (single output).
        assert result == "/mocked_path"
        # The value is written into the store. The target selector is Dropdown(multi=True), so "Europe" -> ["Europe"].
        assert controls_store["filter_page_2_show_in_url_true"]["currentValue"] == ["Europe"]
        set_props_mock.assert_called_once_with("vizro_controls_store", {"data": controls_store})

    def test_function_control_model_on_different_page_sync(self, mocker):
        # A control-selector trigger targeting a control on another page is a sync (not a drill-through): it writes the
        # value into the controls store and returns no_update so the page does not change.
        action = set_control(control="filter_page_2_show_in_url_true", value="Europe")
        model_manager["button_1"].actions = action
        action.pre_build()
        # Simulate a control-selector trigger (which does not navigate).
        action._is_drill_through = False

        set_props_mock = mocker.patch.object(set_control_module, "set_props")

        controls_store = {"filter_page_2_show_in_url_true": {"currentValue": None}}
        result = action.function(_trigger=None, _controls_store=controls_store)

        # Syncing controls does not navigate.
        assert result is no_update
        assert controls_store["filter_page_2_show_in_url_true"]["currentValue"] == ["Europe"]
        set_props_mock.assert_called_once_with("vizro_controls_store", {"data": controls_store})

    def test_function_reset_with_stale_store_falls_back_to_selector_value(self):
        # A persisted (storage_type="session") store can be stale after a control is added/renamed, so the control's
        # key may be missing. Resetting (value=None) must fall back to the selector's build-time value instead of
        # raising KeyError. The result with an empty store must match the result with an explicit originalValue entry.
        action = set_control(control="filter_page_1", value=None)
        model_manager["button_1"].actions = action
        action.pre_build()

        selector_value = model_manager["filter_page_1"].selector.value

        result_missing = action.function(_trigger=None, _controls_store={})
        result_with_store = action.function(
            _trigger=None,
            _controls_store={"filter_page_1": {"originalValue": selector_value}},
        )

        assert result_missing == result_with_store

    def test_function_cross_page_with_stale_store_rebuilds_full_entry(self, mocker):
        # Cross-page set_control must not raise if the target's key is missing from a stale persisted store. Rather than
        # writing only `currentValue`, it rebuilds the *full* entry so cross-page syncing keeps working (the sync
        # callback needs crossPageTarget/selectorId/etc.), i.e. the store self-heals.
        action = set_control(control="filter_page_2_show_in_url_true", value="Europe")
        model_manager["button_1"].actions = action
        action.pre_build()
        action._is_drill_through = False

        set_props_mock = mocker.patch.object(set_control_module, "set_props")

        control_model = model_manager["filter_page_2_show_in_url_true"]
        controls_store = {}  # stale/empty store missing the target key
        result = action.function(_trigger=None, _controls_store=controls_store)

        assert result is no_update
        # A complete entry is created (mirroring Dashboard._make_page_layout), not just currentValue.
        assert controls_store["filter_page_2_show_in_url_true"] == {
            "currentValue": ["Europe"],
            "originalValue": control_model.selector.value,
            "pageId": "test-page-2",
            "selectorId": control_model.selector.id,
            "showInURL": True,
            "crossPageTarget": True,
        }
        set_props_mock.assert_called_once_with("vizro_controls_store", {"data": controls_store})

    def test_function_multiple_controls_same_page(self):
        # Two same-page targets: the value is shaped per selector and returned as a positionally-aligned list matching
        # `outputs`. filter_page_1 is multi ("Europe" -> ["Europe"]); filter_page_1_single_select is single ("Europe").
        action = set_control(control=["filter_page_1", "filter_page_1_single_select"], value="Europe")
        model_manager["button_1"].actions = action
        action.pre_build()

        result = action.function(_trigger=None, _controls_store={})

        assert result == [["Europe"], "Europe"]

    def test_function_multiple_controls_same_page_per_control_no_update(self):
        # A value that cannot be applied to one target contributes no_update at that position only; the others still
        # update. A 2-item list goes into filter_page_1 (multi) as-is, but a single-value selector cannot take it.
        action = set_control(control=["filter_page_1", "filter_page_1_single_select"], value=["Asia", "Europe"])
        model_manager["button_1"].actions = action
        action.pre_build()

        result = action.function(_trigger=None, _controls_store={})

        assert result == [["Asia", "Europe"], no_update]

    def test_function_mixed_same_and_cross_page_drill_through_does_not_navigate(self, mocker):
        # A drill-through (figure trigger) with one same-page target (returned via the callback output) and one
        # cross-page target (written to the store) does NOT navigate: a same-page target means the user stays on the
        # current page (its selector is updated live, the cross-page value is applied from the store when that page is
        # opened). The returned list is aligned to `outputs` = [filter_page_1, "vizro_url.pathname"], so the trailing
        # pathname slot stays no_update.
        action = set_control(control=["filter_page_1", "filter_page_2_show_in_url_true"], value="Europe")
        model_manager["button_1"].actions = action
        action.pre_build()
        assert action._is_drill_through is True
        assert action._drill_through_path is None

        get_relative_path_mock = mocker.patch.object(set_control_module, "get_relative_path")
        set_props_mock = mocker.patch.object(set_control_module, "set_props")

        controls_store = {"filter_page_2_show_in_url_true": {"currentValue": None}}
        result = action.function(_trigger=None, _controls_store=controls_store)

        # Same-page value first, then no navigation (a same-page target is present).
        assert result == [["Europe"], no_update]
        get_relative_path_mock.assert_not_called()
        assert controls_store["filter_page_2_show_in_url_true"]["currentValue"] == ["Europe"]
        set_props_mock.assert_called_once_with("vizro_controls_store", {"data": controls_store})

    def test_function_mixed_same_and_cross_page_sync(self, mocker):
        # Selector-triggered mixed sync (not a drill-through): the same-page control is updated via the callback output
        # and the cross-page control is written to the store, but the page does NOT change. The returned list is aligned
        # to `outputs` = [filter_page_1, "vizro_url.pathname"], so the trailing pathname slot stays no_update.
        action = set_control(control=["filter_page_1", "filter_page_2_show_in_url_true"], value="Europe")
        model_manager["button_1"].actions = action
        action.pre_build()
        # Simulate a control-selector trigger (which does not navigate).
        action._is_drill_through = False

        get_relative_path_mock = mocker.patch.object(set_control_module, "get_relative_path")
        set_props_mock = mocker.patch.object(set_control_module, "set_props")

        controls_store = {"filter_page_2_show_in_url_true": {"currentValue": None}}
        result = action.function(_trigger=None, _controls_store=controls_store)

        # Same-page value first, then no navigation (sync, not drill-through).
        assert result == [["Europe"], no_update]
        get_relative_path_mock.assert_not_called()
        assert controls_store["filter_page_2_show_in_url_true"]["currentValue"] == ["Europe"]
        set_props_mock.assert_called_once_with("vizro_controls_store", {"data": controls_store})


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
        # Cross-page set_control writes to the controls store via set_props; the single callback output is
        # vizro_url.pathname, used to navigate on drill-through (and returned as no_update for a control sync).
        action = set_control(control="filter_page_2_show_in_url_true", value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action.outputs == ["vizro_url.pathname"]

    def test_outputs_multiple_controls_same_page(self):
        # All targets on the same page: outputs is the ordered list of their ids (each a callback output).
        action = set_control(control=["filter_page_1", "filter_page_1_single_select"], value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action.outputs == ["filter_page_1", "filter_page_1_single_select"]

    def test_outputs_mixed_same_and_cross_page(self):
        # Same-page ids are real outputs; the single trailing vizro_url.pathname covers all cross-page targets.
        action = set_control(control=["filter_page_1", "filter_page_2_show_in_url_true"], value="Europe")
        model_manager["button_1"].actions = action

        action.pre_build()

        assert action.outputs == ["filter_page_1", "vizro_url.pathname"]


@pytest.mark.usefixtures("managers_page_hierarchical_filter_set_control")
class TestSetControlHierarchicalFilter:
    def test_pre_build_same_page_leaf_mode_allowed(self):
        # Leaf-mode (full_path=False) hierarchical filter: set_control is allowed.
        action = set_control(control="hier_set_filter", value="Germany")
        model_manager["hier_set_btn"].actions = action
        action.pre_build()
        assert action._same_page_controls == ["hier_set_filter"]


@pytest.mark.usefixtures("managers_page_hierarchical_filter_set_control_path")
class TestSetControlHierarchicalFilterPathMode:
    def test_pre_build_path_mode_raises(self):
        # Path-mode (full_path=True) hierarchical filter: set_control cannot reconstruct a full path from a
        # trigger's single column value, so it is disabled at pre_build.
        action = set_control(control="hier_set_filter_path", value="Germany")
        model_manager["hier_set_btn_path"].actions = action
        with pytest.raises(ValueError, match="full_path=True"):
            action.pre_build()


@pytest.mark.usefixtures("managers_three_pages_for_set_control")
class TestSetControlMultiPage:
    """Drill-through navigates only when every cross-page target resolves to a single, unambiguous page."""

    def test_pre_build_multi_page_targets_have_no_navigation(self):
        # Two cross-page targets on two different pages: the destination is ambiguous, so no navigation path is set.
        action = set_control(control=["filter_a", "filter_b"], value="Europe")
        model_manager["src_button"].actions = action

        action.pre_build()

        assert action._cross_page_controls == ["filter_a", "filter_b"]
        assert action._is_drill_through is True
        assert action._drill_through_path is None

    def test_function_multi_page_targets_do_not_navigate(self, mocker):
        # A drill-through spanning several pages writes every value to the store but does NOT navigate (there is no
        # single "detail view" and only one vizro_url). get_relative_path must not be called.
        action = set_control(control=["filter_a", "filter_b"], value="Europe")
        model_manager["src_button"].actions = action
        action.pre_build()

        get_relative_path_mock = mocker.patch.object(set_control_module, "get_relative_path")
        set_props_mock = mocker.patch.object(set_control_module, "set_props")

        controls_store = {}
        result = action.function(_trigger=None, _controls_store=controls_store)

        # Single output (vizro_url.pathname) and no navigation.
        assert result is no_update
        get_relative_path_mock.assert_not_called()
        # Both cross-page targets are written to the store for pickup on page open.
        assert controls_store["filter_a"]["currentValue"] == ["Europe"]
        assert controls_store["filter_b"]["currentValue"] == ["Europe"]
        set_props_mock.assert_called_once_with("vizro_controls_store", {"data": controls_store})

    def test_outputs_multi_page_targets(self):
        # No same-page targets and at least one cross-page target: the only output is the shared vizro_url.pathname.
        action = set_control(control=["filter_a", "filter_b"], value="Europe")
        model_manager["src_button"].actions = action

        action.pre_build()

        assert action.outputs == ["vizro_url.pathname"]
