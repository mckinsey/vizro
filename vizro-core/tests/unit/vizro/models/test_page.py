import pytest
from pydantic import ValidationError

import vizro.models as vm
from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.models._action._actions_chain import ActionsChain


class TestPageInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_page_mandatory_only(self):
        page = vm.Page(title="Page 1", components=[vm.Button(), vm.Button()])
        assert isinstance(page.components[0], vm.Button) and isinstance(page.components[1], vm.Button)
        assert page.layout.grid == [[0], [1]]
        assert page.controls == []
        assert page.title == "Page 1"
        assert page.id == "Page 1"
        assert page.path == "/page-1"
        assert page.actions == []

    def test_create_page_mandatory_and_optional(self):
        page = vm.Page(
            title="Page 1",
            components=[vm.Button(), vm.Button()],
            id="my-id",
            layout=vm.Layout(grid=[[0, 1]]),
            path="my-path",
        )
        assert isinstance(page.components[0], vm.Button) and isinstance(page.components[1], vm.Button)
        assert page.layout.grid == [[0, 1]]
        assert page.controls == []
        assert page.title == "Page 1"
        assert page.id == "my-id"
        assert page.path == "/my-path"
        assert page.actions == []

    def test_mandatory_title_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Page(id="my-id", components=[vm.Button()])

    def test_mandatory_components_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Page(title="Page 1")

    def test_mandatory_components_invalid(self):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.Page(title="Page 5", components=[])

    def test_set_id_duplicate_title_valid(self):
        vm.Page(title="Page 1", components=[vm.Button()], id="my-id-1")
        vm.Page(title="Page 1", components=[vm.Button()], id="my-id-2")

    def test_set_id_duplicate_title_invalid(self):
        with pytest.raises(
            ValueError,
            match="Page with id=Page 1 already exists. Page id is automatically set to the same as the page title. "
            "If you have multiple pages with the same title then you must assign a unique id.",
        ):
            vm.Page(title="Page 1", components=[vm.Button()])
            vm.Page(title="Page 1", components=[vm.Button()])

    @pytest.mark.parametrize(
        "test_path, expected",
        [
            ("this-path-works", "/this-path-works"),
            ("2147abc", "/2147abc"),
            ("this_path_works", "/this_path_works"),
            ("this/path/works", "/this/path/works"),
            (None, "/page-12"),
        ],
    )
    def test_set_path_valid(self, test_path, expected):
        page = vm.Page(title="Page 1/2", components=[vm.Button()], path=test_path)
        assert page.path == expected

    @pytest.mark.parametrize("test_path", ["this needs? fixing*", " this needs fixing", "THIS NEEDS FIXING"])
    def test_set_path_invalid(self, test_path):
        page = vm.Page(title="Page 1", components=[vm.Button()], path=test_path)
        assert page.path == "/this-needs-fixing"

    def test_set_layout_valid(self):
        vm.Page(title="Page 1", components=[vm.Button(), vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    def test_set_layout_invalid(self):
        with pytest.raises(ValidationError, match="Number of page and grid components need to be the same."):
            vm.Page(title="Page 4", components=[vm.Button()], layout=vm.Layout(grid=[[0, 1]]))


# TODO: Remove this if we can get rid of on-page-load action
class TestPagePreBuildMethod:
    def test_action_auto_generation_valid(self, standard_px_chart):
        page = vm.Page(title="Page 1", components=[vm.Graph(id="scatter_chart", figure=standard_px_chart)])
        page.pre_build()
        assert len(page.actions) == 1
        assert isinstance(page.actions[0], ActionsChain)
        assert page.actions[0].id == f"{ON_PAGE_LOAD_ACTION_PREFIX}_Page 1"
