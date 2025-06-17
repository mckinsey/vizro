from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.io as pio
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro
import vizro.models as vm
from vizro import Vizro
from vizro.actions._action_loop._action_loop import ActionLoop
from vizro.models._dashboard import _all_hidden


class TestDashboardInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_dashboard_mandatory_only(self, page_1, page_2):
        dashboard = vm.Dashboard(pages=[page_1, page_2])
        assert hasattr(dashboard, "id")
        assert dashboard.pages == [page_1, page_2]
        assert dashboard.theme == "vizro_dark"
        assert dashboard.title == ""
        assert isinstance(dashboard.navigation, vm.Navigation)
        assert dashboard.navigation.pages == ["Page 1", "Page 2"]

    def test_create_dashboard_mandatory_and_optional(self, page_1, page_2):
        dashboard = vm.Dashboard(pages=[page_1, page_2], theme="vizro_light", title="Vizro")
        assert hasattr(dashboard, "id")
        assert dashboard.pages == [page_1, page_2]
        assert dashboard.theme == "vizro_light"
        assert dashboard.title == "Vizro"
        assert isinstance(dashboard.navigation, vm.Navigation)
        assert dashboard.navigation.pages == ["Page 1", "Page 2"]

    def test_navigation_pages_automatically_populated(self, page_1, page_2):
        dashboard = vm.Dashboard(pages=[page_1, page_2])
        assert dashboard.navigation.pages == ["Page 1", "Page 2"]

    def test_navigation_with_pages(self, page_1, page_2):
        dashboard = vm.Dashboard(pages=[page_1, page_2], navigation=vm.Navigation(pages=["Page 1"]))
        assert dashboard.navigation.pages == ["Page 1"]

    def test_mandatory_pages_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Dashboard()

    def test_field_invalid_pages_empty_list(self):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.Dashboard(pages=[])

    def test_field_invalid_pages_input_type(self):
        with pytest.raises(ValidationError, match="Input should be a valid dictionary or instance of Page"):
            vm.Dashboard(pages=[vm.Button()])

    def test_field_invalid_theme_input_type(self, page_1):
        with pytest.raises(ValidationError, match="Input should be 'vizro_dark' or 'vizro_light'"):
            vm.Dashboard(pages=[page_1], theme="not_existing")


class TestDashboardPreBuild:
    """Tests dashboard pre_build method."""

    def test_page_registry(self, vizro_app, page_1, page_2, mocker):
        mock_register_page = mocker.patch("dash.register_page", autospec=True)
        mock_make_page_404_layout = mocker.patch(
            "vizro.models._dashboard.Dashboard._make_page_404_layout"
        )  # Checking the actual dash components is done in test_make_page_404_layout.
        vm.Dashboard(pages=[page_1, page_2]).pre_build()

        mock_register_page.assert_any_call(
            module=page_1.id,
            name="Page 1",
            description=None,
            image=None,
            title="Page 1",
            path="/",
            order=0,
            layout=mocker.ANY,  # partial call is tricky to mock out so we ignore it.
        )
        mock_register_page.assert_any_call(
            module=page_2.id,
            name="Page 2",
            description=None,
            image=None,
            title="Page 2",
            path="/page-2",
            order=1,
            layout=mocker.ANY,  # partial call is tricky to mock out so we ignore it.
        )
        mock_register_page.assert_any_call(module="not_found_404", layout=mock_make_page_404_layout())
        assert mock_register_page.call_count == 3

    def test_page_registry_with_dashboard_title(self, vizro_app, page_1, mocker):
        mock_register_page = mocker.patch("dash.register_page", autospec=True)
        vm.Dashboard(pages=[page_1], title="My dashboard").pre_build()

        mock_register_page.assert_any_call(
            module=page_1.id,
            name="Page 1",
            description=None,
            image=None,
            title="My dashboard: Page 1",
            path="/",
            order=0,
            layout=mocker.ANY,  # partial call is tricky to mock out so we ignore it.
        )

    def test_page_registry_with_dashboard_description(self, vizro_app, page_1, mocker):
        mock_register_page = mocker.patch("dash.register_page", autospec=True)
        vm.Dashboard(pages=[page_1], description="Dashboard description").pre_build()

        mock_register_page.assert_any_call(
            module=page_1.id,
            name="Page 1",
            description="Dashboard description",
            image=None,
            title="Page 1",
            path="/",
            order=0,
            layout=mocker.ANY,  # partial call is tricky to mock out so we ignore it.
        )

    def test_page_registry_with_page_description(self, vizro_app, mocker):
        mock_register_page = mocker.patch("dash.register_page", autospec=True)
        vm.Dashboard(
            pages=[vm.Page(title="Page 1", components=[vm.Button()], description="Page description")]
        ).pre_build()

        mock_register_page.assert_any_call(
            module="Page 1",
            name="Page 1",
            description="Page description",
            image=None,
            title="Page 1",
            path="/",
            order=0,
            layout=mocker.ANY,  # partial call is tricky to mock out so we ignore it.
        )

    def test_page_registry_with_dashboard_and_page_description(self, vizro_app, mocker):
        mock_register_page = mocker.patch("dash.register_page", autospec=True)
        vm.Dashboard(
            description="Dashboard description",
            pages=[vm.Page(title="Page 1", components=[vm.Button()], description="Page description")],
        ).pre_build()

        mock_register_page.assert_any_call(
            module="Page 1",
            name="Page 1",
            description="Page description",
            image=None,
            title="Page 1",
            path="/",
            order=0,
            layout=mocker.ANY,  # partial call is tricky to mock out so we ignore it.
        )

    @pytest.mark.parametrize(
        "image_path", ["app.png", "app.svg", "images/app.png", "images/app.svg", "logo.png", "logo.svg"]
    )
    def test_page_registry_with_image(self, page_1, mocker, tmp_path, image_path):
        if Path(image_path).parent != Path("."):
            Path(tmp_path / image_path).parent.mkdir()
        Path(tmp_path / image_path).touch()
        Vizro(assets_folder=tmp_path)
        mock_register_page = mocker.patch("dash.register_page", autospec=True)
        vm.Dashboard(pages=[page_1]).pre_build()

        mock_register_page.assert_any_call(
            module=page_1.id,
            name="Page 1",
            description=None,
            image=image_path,
            title="Page 1",
            path="/",
            order=0,
            layout=mocker.ANY,  # partial call is tricky to mock out so we ignore it.
        )

    # TODO: Move the test to `TestDashboardBuild` once asset_component_equal is implemented for dashboard build method
    @pytest.mark.parametrize(
        "image_path",
        [
            "logo.svg",
            "logo.png",
            "logo.apng",
            "logo.avif",
            "logo.gif",
            "logo.jpeg",
            "logo.jpg",
            "logo.webp",
            "images/logo.svg",
        ],
    )
    def test_infer_image(self, page_1, tmp_path, image_path):
        if Path(image_path).parent != Path("."):
            Path(tmp_path / image_path).parent.mkdir()

        Path(tmp_path / image_path).touch()
        Vizro(assets_folder=tmp_path)
        vm.Dashboard(pages=[page_1]).pre_build()

        assert_component_equal(vm.Dashboard._infer_image("logo"), image_path)

    def test_page_registry_with_images(self, page_1, mocker, tmp_path):
        Path(tmp_path / "app.svg").touch()
        Path(tmp_path / "logo.svg").touch()
        Vizro(assets_folder=tmp_path)
        mock_register_page = mocker.patch("dash.register_page", autospec=True)
        vm.Dashboard(pages=[page_1]).pre_build()

        mock_register_page.assert_any_call(
            module=page_1.id,
            name="Page 1",
            description=None,
            image="app.svg",
            title="Page 1",
            path="/",
            order=0,
            layout=mocker.ANY,  # partial call is tricky to mock out so we ignore it.
        )

    @pytest.mark.parametrize(
        "logo_files, error_msg",
        [
            (
                ["logo.svg", "logo_dark.svg", "logo_light.svg"],
                "Cannot provide `logo` together with both `logo_dark` and `logo_light`. Please provide either `logo`, "
                "or both `logo_dark` and `logo_light`.",
            ),
            (
                ["logo.svg", "logo_light.svg"],
                "Both `logo_dark` and `logo_light` must be provided together. Please provide either both or neither.",
            ),
            (
                ["logo.svg", "logo_dark.svg"],
                "Both `logo_dark` and `logo_light` must be provided together. Please provide either both or neither.",
            ),
            (
                ["logo_light.svg"],
                "Both `logo_dark` and `logo_light` must be provided together. Please provide either both or neither.",
            ),
            (
                ["logo_dark.svg"],
                "Both `logo_dark` and `logo_light` must be provided together. Please provide either both or neither.",
            ),
        ],
    )
    def test_invalid_logo_combinations(self, page_1, tmp_path, logo_files, error_msg):
        for file_path in logo_files:
            Path(tmp_path / file_path).touch()
        Vizro(assets_folder=tmp_path)

        with pytest.raises(ValueError, match=error_msg):
            vm.Dashboard(pages=[page_1]).pre_build()

    @pytest.mark.parametrize(
        "logo_files",
        [["logo_dark.svg", "logo_light.svg"], ["logo.svg"], []],
    )
    def test_valid_logo_combinations(self, page_1, tmp_path, logo_files):
        for file_path in logo_files:
            Path(tmp_path / file_path).touch()
        Vizro(assets_folder=tmp_path)
        vm.Dashboard(pages=[page_1]).pre_build()

    def test_make_page_404_layout(self, page_1, vizro_app):
        # vizro_app fixture is needed to avoid mocking out get_relative_path.
        expected = html.Div(
            [
                dbc.Switch(
                    id="theme-selector",
                    value=False,
                    persistence=True,
                    persistence_type="session",
                ),
                html.Img(),
                html.H3("This page could not be found."),
                html.P("Make sure the URL you entered is correct."),
                dbc.Button(children="Take me home", href="/", class_name="mt-4"),
            ],
            className="d-flex flex-column align-items-center justify-content-center min-vh-100",
        )
        # Strip out src since it's too long to be worth comparing and just comes directly from reading a file.
        assert_component_equal(vm.Dashboard(pages=[page_1])._make_page_404_layout(), expected, keys_to_strip={"src"})


class TestDashboardBuild:
    """Tests dashboard build method."""

    def test_dashboard_build(self, vizro_app, page_1, page_2):
        dashboard = vm.Dashboard(pages=[page_1, page_2])
        dashboard.pre_build()

        # Test application of template_dashboard_overrides.
        dashboard_vizro_dark = pio.templates["vizro_dark"]
        dashboard_vizro_dark.layout.update(
            geo_bgcolor="rgba(0, 0, 0, 0)",
            geo_lakecolor="rgba(0, 0, 0, 0)",
            geo_landcolor="rgba(0, 0, 0, 0)",
            margin_b=16,
            margin_l=24,
            margin_t=24,
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            polar_bgcolor="rgba(0, 0, 0, 0)",
            ternary_bgcolor="rgba(0, 0, 0, 0)",
            title_pad_l=0,
            title_pad_r=0,
        )
        dashboard_vizro_light = pio.templates["vizro_light"]
        dashboard_vizro_light.layout.update(
            geo_bgcolor="rgba(0, 0, 0, 0)",
            geo_lakecolor="rgba(0, 0, 0, 0)",
            geo_landcolor="rgba(0, 0, 0, 0)",
            margin_b=16,
            margin_l=24,
            margin_t=24,
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            polar_bgcolor="rgba(0, 0, 0, 0)",
            ternary_bgcolor="rgba(0, 0, 0, 0)",
            title_pad_l=0,
            title_pad_r=0,
        )

        expected_dashboard_container = dmc.MantineProvider(
            children=[
                html.Div(
                    id="dashboard-container",
                    children=[
                        html.Div(id="vizro_version", children=vizro.__version__, hidden=True),
                        dcc.Store(
                            id="vizro_themes",
                            data={
                                "vizro_dark": dashboard_vizro_dark,
                                "vizro_light": dashboard_vizro_light,
                            },
                        ),
                        ActionLoop._create_app_callbacks(),
                        dash.page_container,
                    ],
                )
            ],
            theme={"primaryColor": "gray"},
        )
        assert_component_equal(dashboard.build(), expected_dashboard_container)


@pytest.mark.parametrize(
    "components, expected",
    [
        ([html.Div(hidden=False)], False),
        ([html.Div(id="children-id")], False),
        ([html.Div(hidden=True), None, html.Div(hidden=False)], False),
        ([html.Div(hidden=True), None, html.Div(id="children-id")], False),
        ([html.Div(hidden=True)], True),
        ([None], True),
        ([html.Div(hidden=True), None], True),
    ],
)
def test_get_hideable_parent_div_visible(components, expected):
    assert _all_hidden(components) == expected
