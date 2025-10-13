import pytest
from asserts import assert_component_equal
from dash import dcc, html

import vizro.models as vm
from vizro.actions._parameter_action import _parameter
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
        with pytest.raises(
            ValueError,
            match=r"Invalid target scatter_chart. "
            "Targets must be supplied in the form <target_component>.<target_argument>",
        ):
            Parameter(targets=["scatter_chart"], selector=vm.Dropdown(options=["lifeExp", "pop"]))

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
        with pytest.raises(ValueError, match=r"Control parameter_id should be defined within a Page object."):
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
    def test_targets_present_invalid(self):
        parameter = Parameter(targets=["scatter_chart_invalid.x"], selector=vm.Dropdown(options=["lifeExp", "pop"]))
        model_manager["test_page"].controls = [parameter]
        with pytest.raises(ValueError, match=r"Target scatter_chart_invalid not found within the test_page."):
            parameter.pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize("test_input", [vm.Slider(), vm.RangeSlider(), vm.DatePicker()])
    def test_numerical_and_temporal_selectors_missing_values(self, test_input):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        with pytest.raises(
            TypeError, match=f"{test_input.type} requires the arguments 'min' and 'max' when used within Parameter."
        ):
            parameter.pre_build()

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

        assert isinstance(default_action, _parameter)
        assert default_action.id == f"__parameter_action_{parameter.id}"
        assert default_action.targets == ["scatter_chart.x"]

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

    @pytest.mark.usefixtures("managers_one_page_two_graphs_with_dynamic_data")
    @pytest.mark.parametrize(
        "filter_targets, expected_parameter_targets",
        [
            ([], {"scatter_chart.data_frame.first_n"}),
            (["scatter_chart"], {"scatter_chart.data_frame.first_n", "filter_id", "scatter_chart"}),
            (
                ["scatter_chart", "box_chart"],
                {"scatter_chart.data_frame.first_n", "filter_id", "scatter_chart", "box_chart"},
            ),
        ],
    )
    def test_targets_argument_for_data_frame_parameter_action(
        self, filter_targets, expected_parameter_targets, gapminder_dynamic_first_n_last_n_function
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
        assert set(default_action.targets) == expected_parameter_targets

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
