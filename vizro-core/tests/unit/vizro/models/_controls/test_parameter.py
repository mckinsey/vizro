import pytest
from asserts import assert_component_equal
from dash import dcc, html

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions._set_control import set_control
from vizro.actions._update_targets import update_targets
from vizro.managers import data_manager, model_manager
from vizro.models._controls.parameter import Parameter


@pytest.mark.usefixtures("managers_one_page_two_graphs")
class TestParameterInstantiation:
    def test_create_parameter_mandatory_only(self):
        parameter = Parameter(
            id="parameter_id",
            targets=["scatter_chart.x"],
            selector=vm.Dropdown(
                id="selector_id",
                options=["lifeExp", "gdpPercap", "pop"],
                multi=False,
                value="lifeExp",
                title="Choose x-axis",
            ),
        )
        assert parameter.type == "parameter"
        assert parameter.targets == ["scatter_chart.x"]
        assert parameter.selector.type == "dropdown"
        assert parameter._action_triggers == {"__default__": "selector_id.value"}
        assert parameter._action_outputs == {
            "__default__": "selector_id.value",
            "selector": "parameter_id.children",
            "title": "selector_id_title.children",
        }
        assert parameter._action_inputs == {"__default__": "selector_id.value"}

    def test_create_parameter_mandatory_and_optional(self):
        parameter = Parameter(
            id="parameter_id",
            targets=["scatter_chart.x"],
            selector=vm.Dropdown(
                id="selector_id",
                options=["lifeExp", "gdpPercap", "pop"],
                multi=False,
                value="lifeExp",
                title="Choose x-axis",
                description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
            ),
            show_in_url=True,
        )
        assert parameter.id == "parameter_id"
        assert parameter.type == "parameter"
        assert parameter.targets == ["scatter_chart.x"]
        assert parameter.selector.type == "dropdown"
        assert parameter.show_in_url is True
        assert isinstance(parameter.selector.description, vm.Tooltip)
        assert parameter._action_triggers == {"__default__": "selector_id.value"}
        assert parameter._action_outputs == {
            "__default__": "selector_id.value",
            "selector": "parameter_id.children",
            "title": "selector_id_title.children",
            "description": "tooltip-id-text.children",
        }
        assert parameter._action_inputs == {
            "__default__": "selector_id.value",
        }

    def test_check_dot_notation_failed(self):
        # The model-level `check_dot_notation` validator now lets non-dotted targets through so that control ids
        # (Filter/Parameter) can be used as targets. A non-dotted target that is *not* another control is therefore
        # only rejected later, in pre_build.
        parameter = Parameter(targets=["scatter_chart"], selector=vm.Dropdown(options=["lifeExp", "pop"]))
        model_manager["test_page"].controls = [parameter]
        with pytest.raises(
            ValueError,
            match=r"Invalid target scatter_chart. "
            "Targets must be supplied in the form <target_component>.<target_argument>",
        ):
            parameter.pre_build()

    @pytest.mark.parametrize("target", ["scatter_chart.figure", "scatter_chart.figure.color"])
    def test_check_dot_notation_figure_argument_failed(self, target):
        # A dotted target that addresses the CapturedCallable via `.figure` is still rejected at construction time,
        # both as the exact `<component>.figure` and as a nested `<component>.figure.<arg>`.
        with pytest.raises(
            ValueError,
            match=rf"Invalid target {target}. Targets must be supplied in the form "
            "<target_component>.<target_argument>. Arguments of the CapturedCallable function can be targeted "
            "directly, and not via <.figure.>.",
        ):
            Parameter(targets=[target], selector=vm.Dropdown(options=["lifeExp", "pop"]))

    @pytest.mark.parametrize("target", ["scatter_chart.data_frame", "scatter_chart.data_frame.argument.nested_arg"])
    def test_check_data_frame_as_target_argument_failed(self, target):
        with pytest.raises(
            ValueError,
            match=f"Invalid target {target}. 'data_frame' target must be supplied in the form "
            f"<target_component>.data_frame.<dynamic_data_argument>",
        ):
            Parameter(targets=[target], selector=vm.Dropdown(options=["lifeExp", "pop"]))

    def test_duplicate_parameter_target_failed(self):
        with pytest.raises(ValueError, match=r"Duplicate parameter targets {'scatter_chart.x'} found."):
            Parameter(targets=["scatter_chart.x", "scatter_chart.x"], selector=vm.Dropdown(options=["lifeExp", "pop"]))

    def test_duplicate_parameter_target_failed_two_params(self):
        with pytest.raises(ValueError, match=r"Duplicate parameter targets {'scatter_chart.x'} found."):
            Parameter(targets=["scatter_chart.x"], selector=vm.Dropdown(options=["lifeExp", "pop"]))
            Parameter(targets=["scatter_chart.x"], selector=vm.Dropdown(options=["lifeExp", "pop"]))

    def test_missing_id_for_url_control_warning_raised(self):
        with pytest.warns(
            UserWarning,
            match="`show_in_url=True` is set but no `id` was provided. "
            "Shareable URLs might be unreliable if your dashboard configuration changes in future. "
            "If you want to ensure that links continue working, set a fixed `id`.",
        ):
            Parameter(
                targets=["scatter_chart.x"],
                selector=vm.Dropdown(options=["lifeExp", "pop"]),
                show_in_url=True,
            )


class TestPreBuildMethod:
    def test_parameter_not_in_page(self):
        with pytest.raises(
            ValueError, match=r"Control parameter_id should be defined within Page.controls or Container.controls."
        ):
            Parameter(
                id="parameter_id",
                targets=["scatter_chart.x"],
                selector=vm.Dropdown(options=["lifeExp", "pop"]),
            ).pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize(
        "test_input, title",
        [
            (vm.Checklist(options=["lifeExp", "gdpPercap", "pop"], value=["lifeExp"]), "x"),
            (vm.Dropdown(options=["lifeExp", "gdpPercap", "pop"], multi=False, value="lifeExp"), "x"),
            (
                vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"], value="lifeExp", title="Choose x-axis"),
                "Choose x-axis",
            ),
        ],
    )
    def test_set_target_and_title_valid(self, test_input, title):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        parameter.pre_build()
        assert parameter.targets == ["scatter_chart.x"]
        assert parameter.selector.title == title

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    def test_set_target_wrapped_parameter_valid(self, MockControlWrapper):
        parameter = Parameter(targets=["scatter_chart.x"], selector=vm.Dropdown(options=["lifeExp", "pop"]))
        model_manager["test_page"].controls = [MockControlWrapper(control=parameter)]
        parameter.pre_build()

        assert parameter.targets == ["scatter_chart.x"]

    @pytest.mark.usefixtures("managers_one_page_container_controls_invalid")
    def test_container_parameter_targets_invalid(self):
        parameter = model_manager["container_parameter"]
        with pytest.raises(
            ValueError,
            match="Target bar_chart not found within the container_1",
        ):
            parameter.pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    def test_targets_present_invalid(self):
        parameter = Parameter(targets=["scatter_chart_invalid.x"], selector=vm.Dropdown(options=["lifeExp", "pop"]))
        model_manager["test_page"].controls = [parameter]
        with pytest.raises(ValueError, match=r"Target scatter_chart_invalid not found within the test_page."):
            parameter.pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize(
        "test_input",
        [
            vm.Slider(),
            vm.RangeSlider(),
            vm.DatePicker(),
            vm.DateTimePicker(),
            vm.DateTimePicker(range=False),
        ],
    )
    def test_numerical_and_temporal_selectors_missing_values(self, test_input):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        with pytest.raises(
            TypeError, match=f"{test_input.type} requires the arguments 'min' and 'max' when used within Parameter."
        ):
            parameter.pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize(
        "test_input, expected_value",
        [
            # Range default is date-only ISO strings derived from min/max (time portion cleared).
            (vm.DateTimePicker(min="2024-01-01", max="2024-12-31"), ["2024-01-01", "2024-12-31"]),
            (vm.DateTimePicker(min="2024-01-01", max="2024-12-31", range=False), "2024-01-01"),
        ],
    )
    def test_datetime_selector_with_min_max_valid(self, test_input, expected_value):
        """DateTimePicker with min/max is accepted in a Parameter and gets a date-only default value."""
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        parameter.pre_build()
        assert parameter.targets == ["scatter_chart.x"]
        assert parameter.selector.value == expected_value

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize("test_input", [vm.Checklist(), vm.Dropdown(), vm.RadioItems()])
    def test_categorical_selectors_with_missing_options(self, test_input):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        with pytest.raises(
            TypeError, match=f"{parameter.selector.type} requires the argument 'options' when used within Parameter."
        ):
            parameter.pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize(
        "test_input",
        [
            (vm.Checklist(options=["lifeExp", "gdpPercap", "pop"], value=["lifeExp"])),
            (vm.Dropdown(options=["lifeExp", "gdpPercap", "pop"], multi=False, value="lifeExp")),
            (vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"], value="lifeExp")),
        ],
    )
    def test_set_actions(self, test_input):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        parameter.pre_build()

        [default_action] = parameter.selector.actions

        assert isinstance(default_action, update_targets)
        assert default_action.id == f"__parameter_action_{parameter.id}"
        assert default_action.targets == ["scatter_chart"]

    def test_set_custom_action(self, managers_one_page_two_graphs, identity_action_function):
        action_function = identity_action_function()
        custom_action = vm.Action(function=action_function)
        parameter = vm.Parameter(
            targets=["scatter_chart.x"],
            selector=vm.RadioItems(
                options=["lifeExp", "gdpPercap", "pop"],
                actions=[custom_action],
            ),
        )
        model_manager["test_page"].controls = [parameter]
        parameter.pre_build()
        assert parameter.selector.actions == [custom_action]

    def test_set_empty_actions(self, managers_one_page_two_graphs):
        # Explicitly empty actions opts out of the default "refresh on change" action, so it must not be overwritten
        # with the default update_targets action.
        parameter = vm.Parameter(
            targets=["scatter_chart.x"],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"], actions=[]),
        )
        model_manager["test_page"].controls = [parameter]
        parameter.pre_build()
        assert parameter.selector.actions == []

    def test_set_empty_actions_from_dict(self, managers_one_page_two_graphs):
        # The same opt-out must be honored through dict/YAML config where `actions: []` is given explicitly.
        parameter = vm.Parameter(
            targets=["scatter_chart.x"],
            selector={"type": "radio_items", "options": ["lifeExp", "gdpPercap", "pop"], "actions": []},
        )
        model_manager["test_page"].controls = [parameter]
        parameter.pre_build()
        assert parameter.selector.actions == []

    def test_set_none_actions(self, managers_one_page_two_graphs):
        # actions=None is equivalent to actions=[]: it also opts out of the default "refresh on change" action.
        parameter = vm.Parameter(
            targets=["scatter_chart.x"],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"], actions=None),
        )
        model_manager["test_page"].controls = [parameter]
        parameter.pre_build()
        assert parameter.selector.actions == []

    def test_set_none_actions_from_dict(self, managers_one_page_two_graphs):
        # The same opt-out must be honored through dict/YAML config where `actions: null` is given explicitly.
        parameter = vm.Parameter(
            targets=["scatter_chart.x"],
            selector={"type": "radio_items", "options": ["lifeExp", "gdpPercap", "pop"], "actions": None},
        )
        model_manager["test_page"].controls = [parameter]
        parameter.pre_build()
        assert parameter.selector.actions == []

    def test_target_control_sync_actions(self, managers_one_page_two_graphs):
        # A Parameter can target another control (a Filter or Parameter) to keep it in sync. The control target is
        # extracted out of self.targets and turned into a `set_control` action that runs *before* the default
        # `update_targets` action so the synced value is applied first.
        target_filter = vm.Filter(id="target_filter", column="continent")
        parameter = vm.Parameter(
            id="source_parameter",
            targets=["scatter_chart.x", "target_filter"],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"]),
        )
        model_manager["test_page"].controls = [target_filter, parameter]
        target_filter.pre_build()
        parameter.pre_build()

        # The control target is removed from self.targets, leaving only the figure-argument target.
        assert parameter.targets == ["scatter_chart.x"]

        set_control_action, update_targets_action = parameter.selector.actions
        assert isinstance(set_control_action, set_control)
        assert set_control_action.control == "target_filter"
        assert set_control_action.value is None
        assert isinstance(update_targets_action, update_targets)
        assert update_targets_action.id == "__parameter_action_source_parameter"
        assert update_targets_action.targets == ["scatter_chart"]

    def test_target_multiple_controls_sync_actions(self, managers_one_page_two_graphs):
        # A Parameter can target several controls at once; one set_control action is generated per control target,
        # in order, all before the single update_targets action.
        target_filter = vm.Filter(id="target_filter", column="continent")
        target_parameter = vm.Parameter(
            id="target_parameter",
            targets=["bar_chart.x"],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"]),
        )
        parameter = vm.Parameter(
            id="source_parameter",
            targets=["scatter_chart.x", "target_filter", "target_parameter"],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"]),
        )
        model_manager["test_page"].controls = [target_filter, target_parameter, parameter]
        target_filter.pre_build()
        target_parameter.pre_build()
        parameter.pre_build()

        assert parameter.targets == ["scatter_chart.x"]
        first, second, update_targets_action = parameter.selector.actions
        assert [a.control for a in (first, second)] == ["target_filter", "target_parameter"]
        assert all(isinstance(a, set_control) and a.value is None for a in (first, second))
        assert isinstance(update_targets_action, update_targets)
        assert update_targets_action.targets == ["scatter_chart"]

    def test_two_parameters_target_same_control_allowed(self, managers_one_page_two_graphs):
        # Two parameters may keep the same control in sync. The shared bare control id is a control-sync target, not a
        # figure-argument target, so it must not trip the duplicate-parameter-target check (which only guards figure
        # arguments, since two parameters writing the same figure argument would conflict).
        target_filter = vm.Filter(id="shared_filter", column="continent")
        parameter_1 = vm.Parameter(
            id="parameter_1",
            targets=["scatter_chart.x", "shared_filter"],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"]),
        )
        parameter_2 = vm.Parameter(
            id="parameter_2",
            targets=["bar_chart.x", "shared_filter"],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"]),
        )
        model_manager["test_page"].controls = [target_filter, parameter_1, parameter_2]
        target_filter.pre_build()
        parameter_1.pre_build()
        parameter_2.pre_build()

        assert parameter_1.selector.actions[0].control == "shared_filter"
        assert parameter_2.selector.actions[0].control == "shared_filter"

    def test_target_control_ignored_with_explicit_actions_warns(
        self, managers_one_page_two_graphs, identity_action_function
    ):
        # A control target is synced by generating a default set_control action on the selector. When the selector
        # has explicit actions, that default chain is skipped, so a control target listed in `targets` is stripped
        # without being synced. This must warn rather than silently do nothing.
        custom_action = vm.Action(function=identity_action_function())
        target_filter = vm.Filter(id="target_filter", column="continent")
        parameter = vm.Parameter(
            id="source_parameter",
            targets=["scatter_chart.x", "target_filter"],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"], actions=[custom_action]),
        )
        model_manager["test_page"].controls = [target_filter, parameter]
        target_filter.pre_build()
        with pytest.warns(
            UserWarning, match=r"Control 'source_parameter' lists control target\(s\) \['target_filter'\]"
        ):
            parameter.pre_build()

        # The control target is still stripped from targets; the user's explicit actions are left untouched.
        assert parameter.targets == ["scatter_chart.x"]
        assert parameter.selector.actions == [custom_action]

    def test_target_control_self_target_invalid(self, managers_one_page_two_graphs):
        # A control targeting itself would create a self-referential sync loop and is rejected.
        parameter = vm.Parameter(
            id="self_parameter",
            targets=["scatter_chart.x", "self_parameter"],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"]),
        )
        model_manager["test_page"].controls = [parameter]
        with pytest.raises(
            ValueError, match=r"Control 'self_parameter' cannot target itself. Remove 'self_parameter' from"
        ):
            parameter.pre_build()

    def test_target_control_different_page_invalid(self, gapminder):
        # A control can only target other controls on the same page (the underlying set_control sync is per-page).
        vm.Page(
            id="page_a",
            title="Page A",
            components=[vm.Graph(id="graph_a", figure=px.scatter(gapminder, x="lifeExp", y="gdpPercap"))],
            controls=[
                vm.Parameter(
                    id="param_a",
                    targets=["graph_a.x", "filter_b"],
                    selector=vm.RadioItems(options=["lifeExp", "gdpPercap"]),
                )
            ],
        )
        vm.Page(
            id="page_b",
            title="Page B",
            components=[vm.Graph(id="graph_b", figure=px.scatter(gapminder, x="lifeExp", y="gdpPercap"))],
            controls=[vm.Filter(id="filter_b", column="continent")],
        )
        with pytest.raises(
            ValueError, match=r"Control 'param_a' cannot target control 'filter_b' because they are on different pages"
        ):
            model_manager["param_a"].pre_build()

    def test_target_only_controls_invalid(self, managers_one_page_two_graphs):
        # A Parameter must have at least one figure target: its value is applied to figures only through its
        # "<component>.<argument>" targets, so targeting only other controls leaves nothing to apply the value to.
        # This restores the pre-syncing behavior where such a (non-dotted) target was rejected by check_dot_notation.
        target_parameter = vm.Parameter(
            id="target_parameter",
            targets=["scatter_chart.x"],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"]),
        )
        parameter = vm.Parameter(
            id="source_parameter",
            targets=["target_parameter"],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"]),
        )
        model_manager["test_page"].controls = [target_parameter, parameter]
        target_parameter.pre_build()
        with pytest.raises(
            ValueError,
            match=r"Parameter 'source_parameter' must have at least one target in the form "
            r"<target_component>.<target_argument>",
        ):
            parameter.pre_build()

    def test_target_empty_invalid(self, managers_one_page_two_graphs):
        # A Parameter with no targets at all likewise has no figure argument to apply its value to and is rejected.
        parameter = vm.Parameter(
            id="empty_parameter",
            targets=[],
            selector=vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"]),
        )
        model_manager["test_page"].controls = [parameter]
        with pytest.raises(
            ValueError,
            match=r"Parameter 'empty_parameter' must have at least one target in the form "
            r"<target_component>.<target_argument>",
        ):
            parameter.pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs_with_dynamic_data")
    @pytest.mark.parametrize(
        "filter_targets, expected_parameter_targets, expected_parameter_action_argument",
        [
            ([], {"scatter_chart.data_frame.first_n"}, {"scatter_chart"}),
            (
                ["scatter_chart"],
                {"scatter_chart.data_frame.first_n", "filter_id", "scatter_chart"},
                {"scatter_chart", "filter_id"},
            ),
            (
                ["scatter_chart", "box_chart"],
                {"scatter_chart.data_frame.first_n", "filter_id", "scatter_chart", "box_chart"},
                {"scatter_chart", "filter_id", "box_chart"},
            ),
        ],
    )
    def test_targets_argument_for_data_frame_parameter_action(
        self,
        filter_targets,
        expected_parameter_targets,
        expected_parameter_action_argument,
        gapminder_dynamic_first_n_last_n_function,
    ):
        data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function

        if filter_targets:
            dynamic_filter = vm.Filter(id="filter_id", column="pop", targets=filter_targets)
            model_manager["test_page"].controls.append(dynamic_filter)
            dynamic_filter.pre_build()

        data_frame_parameter = vm.Parameter(
            id="test_data_frame_parameter",
            targets=["scatter_chart.data_frame.first_n"],
            selector=vm.Slider(id="first_n_parameter", min=1, max=10, step=1),
        )
        model_manager["test_page"].controls.append(data_frame_parameter)
        data_frame_parameter.pre_build()

        [default_action] = data_frame_parameter.selector.actions
        assert set(data_frame_parameter.targets) == expected_parameter_targets
        assert set(default_action.targets) == expected_parameter_action_argument

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    def test_parameter_action_properties(self):
        parameter = Parameter(
            id="parameter_id",
            targets=["scatter_chart.x"],
            selector=vm.Dropdown(
                id="selector_id",
                options=["lifeExp", "gdpPercap", "pop"],
                title="Choose x-axis",
                description=vm.Tooltip(id="selector_tooltip_id", text="Test", icon="info"),
            ),
        )
        model_manager["test_page"].controls = [parameter]
        parameter.pre_build()

        dropdown_properties = dcc.Dropdown().available_properties
        parameter_selector_properties = set(dropdown_properties) - set(html.Div().available_properties)

        assert parameter._action_triggers == {"__default__": "selector_id.value"}
        assert parameter._action_outputs == {
            "__default__": "selector_id.value",
            "selector": "parameter_id.children",
            "title": "selector_id_title.children",
            "description": "selector_tooltip_id-text.children",
            **{prop: f"selector_id.{prop}" for prop in parameter_selector_properties},
        }
        assert parameter._action_inputs == {
            "__default__": "selector_id.value",
            **{prop: f"selector_id.{prop}" for prop in parameter_selector_properties},
        }


@pytest.mark.usefixtures("managers_one_page_two_graphs")
class TestParameterBuild:
    """Tests parameter build method."""

    @pytest.mark.parametrize(
        "test_selector",
        [
            vm.Checklist(options=["lifeExp", "gdpPercap", "pop"]),
            vm.Dropdown(options=["lifeExp", "gdpPercap", "pop"]),
            vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"]),
        ],
    )
    def test_parameter_build(self, test_selector):
        parameter = Parameter(id="parameter-id", targets=["scatter_chart.x"], selector=test_selector)
        page = model_manager["test_page"]
        page.controls = [parameter]
        parameter.pre_build()

        result = parameter.build()
        expected = html.Div(
            id="parameter-id",
            children=html.Div(
                children=[test_selector.build(), dcc.Store(id=f"{test_selector.id}_guard_actions_chain", data=False)]
            ),
            hidden=False,
        )

        assert_component_equal(result, expected)

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize("visible", [True, False])
    def test_parameter_build_visible(self, visible):
        test_selector = vm.Checklist(id="selector_id", options=["lifeExp", "gdpPercap", "pop"])
        parameter = Parameter(id="parameter-id", targets=["scatter_chart.x"], selector=test_selector, visible=visible)
        page = model_manager["test_page"]
        page.controls = [parameter]
        parameter.pre_build()

        result = parameter.build()
        expected = html.Div(
            id="parameter-id",
            children=html.Div(
                children=[test_selector.build(), dcc.Store(id=f"{test_selector.id}_guard_actions_chain", data=False)]
            ),
            hidden=not visible,
        )

        assert_component_equal(result, expected)
