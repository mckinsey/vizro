from typing import Any

import pytest

import vizro.models as vm
from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS


@pytest.fixture
def page_1(standard_px_chart):
    return vm.Page(
        id="page_1_id",
        title="Page 1",
        components=[vm.Button(id="page_1_button_id"), vm.Graph(id="page_1_graph_id", figure=standard_px_chart)],
        controls=[],
    )


@pytest.fixture
def container_1(standard_px_chart):
    return vm.Container(
        id="container_1_id",
        title="Container 1",
        components=[
            vm.Button(id="container_1_button_id"),
            vm.Graph(id="container_1_graph_id", figure=standard_px_chart),
        ],
        controls=[],
    )


@pytest.fixture(autouse=True)
def managers_dashboard_two_pages(vizro_app, page_1, standard_kpi_card):
    return vm.Dashboard(
        pages=[
            page_1,
            vm.Page(
                id="page_2_id",
                title="Page 2",
                components=[
                    vm.Button(id="page_2_button_id"),
                    vm.Figure(id="page_2_figure_id", figure=standard_kpi_card),
                ],
            ),
        ]
    )


class TestGetModels:
    """Test _get_models method."""

    def test_model_type_none_root_model_none(self):
        """model_type is None | page is None -> return all elements."""
        result = [model.id for model in model_manager._get_models()]

        expected = {
            "page_1_id",
            "page_1_button_id",
            "page_1_graph_id",
            "page_2_id",
            "page_2_button_id",
            "page_2_figure_id",
        }

        # model_manager._get_models() returns all models in the dashboard, all along with Layout, Navigation, Dashboard
        # models. That's the reason why we assert with the 'issubset' instead of 'equal'.
        assert expected.issubset(result)

    def test_model_type_root_model_none(self):
        """model_type is vm.Button | root_model is None -> return all vm.Button from the dashboard."""
        result = [model.id for model in model_manager._get_models(model_type=vm.Button)]

        expected = {"page_1_button_id", "page_2_button_id"}
        excluded = {"page_1_id", "page_1_graph_id", "page_2_id", "page_2_figure_id"}

        assert expected.issubset(result)
        assert excluded.isdisjoint(result)

    def test_model_type_none_root_model_not_none(self, page_1):
        """model_type is None | root_model is page_1 -> return all elements from the page_1."""
        result = [model.id for model in model_manager._get_models(root_model=page_1)]

        expected = {"page_1_id", "page_1_button_id", "page_1_graph_id"}
        excluded = {"page_2_id", "page_2_button_id", "page_2_figure_id"}

        assert expected.issubset(result)
        assert excluded.isdisjoint(result)

    def test_model_type_not_none_page_not_none(self, page_1):
        """model_type is vm.Button | page is page_1 -> return all vm.Button from the page_1."""
        result = [model.id for model in model_manager._get_models(model_type=vm.Button, root_model=page_1)]

        expected = {"page_1_button_id"}
        excluded = {"page_1_id", "page_1_graph_id", "page_2_id", "page_2_button_id", "page_2_figure_id"}

        assert expected.issubset(result)
        assert excluded.isdisjoint(result)

    def test_model_type_no_match_root_model_none(self):
        """model_type matches no type | root_model is None -> return empty list."""
        # There is no AgGrid in the dashboard
        result = [model.id for model in model_manager._get_models(model_type=vm.AgGrid)]

        assert result == []

    def test_model_type_no_match_root_model_not_none(self, page_1):
        """model_type matches no type | root_model is page_1 -> return empty list."""
        # There is no AgGrid in the page_1
        result = [model.id for model in model_manager._get_models(model_type=vm.AgGrid, root_model=page_1)]

        assert result == []

    def test_model_type_tuple_of_models(self):
        """model_type is tuple of models -> return all elements of the specified types from the dashboard."""
        result = [model.id for model in model_manager._get_models(model_type=(vm.Button, vm.Graph))]

        expected = {"page_1_button_id", "page_1_graph_id", "page_2_button_id"}
        excluded = {"page_1_id", "page_2_id", "page_2_figure_id"}

        assert expected.issubset(result)
        assert excluded.isdisjoint(result)

    def test_model_type_figure_models(self):
        """model_type is FIGURE_MODELS | root_model is None -> return all figure elements from the dashboard."""
        result = [model.id for model in model_manager._get_models(model_type=FIGURE_MODELS)]

        expected = {"page_1_graph_id", "page_2_figure_id"}
        excluded = {"page_1_id", "page_1_button_id", "page_2_id", "page_2_button_id"}

        assert expected.issubset(result)
        assert excluded.isdisjoint(result)

    def test_subclass_model_type(self, page_1, standard_px_chart):
        """model_type is subclass of vm.Graph -> return all elements of the specified type and its subclasses."""

        class CustomGraph(vm.Graph):
            pass

        page_1.components.append(CustomGraph(id="page_1_custom_graph_id", figure=standard_px_chart))

        # Return CustomGraph and don't return Graph
        custom_graph_result = [model.id for model in model_manager._get_models(model_type=CustomGraph)]
        assert "page_1_custom_graph_id" in custom_graph_result
        assert "page_1_graph_id" not in custom_graph_result

        # Return CustomGraph and Graph
        vm_graph_result = [model.id for model in model_manager._get_models(model_type=vm.Graph)]
        assert "page_1_custom_graph_id" in vm_graph_result
        assert "page_1_graph_id" in vm_graph_result

    # This test checks if the model manager can find model_type under a nested model.
    # Using vm.Filter with a fixed ID as a pytest fixture causes DuplicationID errors during the test collection phase.
    # Lazy instantiation via a lambda avoids this issue.
    @pytest.mark.parametrize(
        "make_nested_control",
        [
            # "x" represents the vm.Filter model that is nested under another model.
            # model as a property of a custom model
            (lambda x: x),
            # model inside a list
            (lambda x: [x]),
            # model as a value in a dictionary
            (lambda x: {"key": x}),
            # model nested in a tuple
            (lambda x: (x,)),
            # model nested within a list of lists
            (lambda x: [[x]]),
            # model nested in a dictionary of dictionaries
            (lambda x: {"key_1": {"key_2": x}}),
            # model nested in a tuple of tuples
            (lambda x: ((x,),)),
        ],
    )
    def test_nested_models(self, page_1, make_nested_control):
        """Model is nested under another model and known property in different ways -> return the model."""

        class ControlGroup(vm.VizroBaseModel):
            controls: Any

        page_1.controls.append(
            ControlGroup(controls=make_nested_control(vm.Filter(id="page_1_control_1", column="year")))
        )

        result = [model.id for model in model_manager._get_models(model_type=vm.Filter, root_model=page_1)]

        assert "page_1_control_1" in result

    def test_model_under_unknown_field(self, page_1):
        """Model is nested under another model but under an unknown field -> don't return the model."""

        class ControlGroup(vm.VizroBaseModel):
            unknown_field: Any

        page_1.controls.append(ControlGroup(unknown_field=vm.Filter(id="page_1_control_1", column="year")))

        result = [model.id for model in model_manager._get_models(model_type=vm.Filter, root_model=page_1)]

        assert "page_1_control_1" not in result

    def test_root_model_container(self, container_1):
        """model_type is None | root_model is container_1 -> return all elements from the container_1."""
        result = [model.id for model in model_manager._get_models(root_model=container_1)]

        expected = {"container_1_id", "container_1_button_id", "container_1_graph_id"}
        excluded = {"page_2_id", "page_2_button_id", "page_2_figure_id"}

        assert expected.issubset(result)
        assert excluded.isdisjoint(result)


class TestGetModelPage:
    """Test _get_model_page method."""

    def test_model_in_page(self, page_1):
        """Model is in page -> return page."""
        result = model_manager._get_model_page(page_1.components[0])

        assert result == page_1

    def test_model_not_in_page(self, page_1):
        """Model is not in page -> return None."""
        # Instantiate standalone model
        button = vm.Button(id="standalone_button_id")

        result = model_manager._get_model_page(button)

        assert result is None

    def test_model_is_page(self, page_1):
        """Model is Page -> return that page."""
        result = model_manager._get_model_page(page_1)

        assert result == page_1
