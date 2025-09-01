import pytest

import vizro.models as vm
from vizro import Vizro
from vizro.actions import collapse_expand_containers
from vizro.managers import model_manager


@pytest.fixture
def managers_one_page_two_containers():
    """Instantiates a model_manager and data_manager with a page and a graph that requires a list input."""
    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Button(id="button"),
            vm.Container(
                id="container_collapsed",
                title="Collapsed container",
                components=[
                    vm.Card(text="Placeholder text"),
                ],
                collapsed=True,
            ),
            vm.Container(
                id="container_expanded",
                title="Expanded container",
                components=[
                    vm.Card(text="Placeholder text"),
                ],
                collapsed=False,
            ),
        ],
    )
    Vizro._pre_build()


@pytest.mark.usefixtures("managers_one_page_two_containers")
class TestCollapseExpandContainersActionInstantiation:
    def test_invalid_duplicate_collapse_expand(self):
        with pytest.raises(
            ValueError, match="`collapse` and `expand` cannot both contain the same IDs {'container_collapsed'}."
        ):
            model_manager["button"].actions = [
                collapse_expand_containers(
                    id="test_action", collapse=["container_collapsed"], expand=["container_collapsed"]
                )
            ]

    def test_invalid_no_collapse_expand(self):
        with pytest.raises(
            ValueError, match="Either the `collapse` or `expand` list must contain at least a single element."
        ):
            model_manager["button"].actions = [collapse_expand_containers(id="test_action")]


@pytest.mark.usefixtures("managers_one_page_two_containers")
class TestCollapseExpandContainersActionPreBuild:
    """Tests collapse_expand_containers pre_build method."""

    def test_pre_build(self):
        # Add action to relevant component
        model_manager["button"].actions = [
            collapse_expand_containers(
                id="test_action", collapse=["container_expanded"], expand=["container_collapsed"]
            )
        ]
        action = model_manager["test_action"]

        # Run pre_build method
        action.pre_build()

        assert set(action.collapse) == {"container_expanded"}
        assert set(action.expand) == {"container_collapsed"}

    def test_pre_build_invalid_collapse_expand(self):
        # Add action to relevant component
        model_manager["button"].actions = [collapse_expand_containers(id="test_action", collapse=["invalid_target_id"])]
        action = model_manager["test_action"]

        with pytest.raises(
            ValueError,
            match=r"Invalid component IDs found: {'invalid_target_id'}."
            " Action's collapse and expand IDs must be collapsible containers on the "
            "same page as the action.",
        ):
            action.pre_build()


@pytest.mark.usefixtures("managers_one_page_two_containers")
class TestCollapseExpandContainersFunction:
    """Tests collapse_expand_containers functionality."""

    def test_collapse_expand_container_function(self):
        # Add action to relevant component
        model_manager["button"].actions = [
            collapse_expand_containers(
                id="test_action", collapse=["container_expanded"], expand=["container_collapsed"]
            )
        ]
        action = model_manager["test_action"]
        action.pre_build()
        # Run action by picking the above added action function and executing it with ()
        result = action.function()

        expected = {"container_expanded": True, "container_collapsed": False}

        assert result == expected
