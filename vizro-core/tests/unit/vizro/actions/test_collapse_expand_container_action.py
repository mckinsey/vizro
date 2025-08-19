import pytest

from vizro.actions import collapse_expand_containers
from vizro.managers import model_manager


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

    def test_pre_build_invalid_no_collapse_expand(self):
        # Add action to relevant component
        model_manager["button"].actions = [collapse_expand_containers(id="test_action")]
        action = model_manager["test_action"]

        with pytest.raises(ValueError, match="At least one of 'collapse' or 'expand' lists must be defined."):
            action.pre_build()

    def test_pre_build_invalid_collapse_expand(self):
        # Add action to relevant component
        model_manager["button"].actions = [collapse_expand_containers(id="test_action", collapse=["test_page"])]
        action = model_manager["test_action"]

        with pytest.raises(ValueError):
            action.pre_build()

    def test_pre_build_invalid_duplicate_collapse_expand(self):
        # Add action to relevant component
        model_manager["button"].actions = [
            collapse_expand_containers(
                id="test_action", collapse=["container_collapsed"], expand=["container_collapsed"]
            )
        ]
        action = model_manager["test_action"]

        with pytest.raises(ValueError, match="Collapse and expand lists cannot contain the same elements!"):
            action.pre_build()


class TestCollapseExpandContainersFunction:
    """Tests collapse_expand_containers functionality."""

    pass
