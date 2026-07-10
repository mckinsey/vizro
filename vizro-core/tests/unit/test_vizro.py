import operator

import dash
import pytest
from dash import html
from packaging.version import parse

import vizro
import vizro.models as vm
from vizro import Vizro
from vizro._constants import VIZRO_ASSETS_PATH
from vizro._vizro import _add_vizro_logs_offcanvas

_git_branch = vizro.__version__ if not parse(vizro.__version__).is_devrelease else "main"


def test_vizro_bootstrap():
    assert (
        vizro.bootstrap
        == f"https://cdn.jsdelivr.net/gh/mckinsey/vizro@{_git_branch}/vizro-core/src/vizro/static/css/vizro-bootstrap.min.css"
    )


# Using Vizro as a framework should include both the library and framework resources, that is, all files in
# VIZRO_ASSETS_PATH.
class TestVizroResources:
    # Only external_url or relative_package_path will exist in the resource specification depending on
    # whether serve_locally=True (the Dash and Vizro default) or False.
    @pytest.mark.parametrize(
        "serve_locally, resource_key, resource_value",
        [
            (True, "relative_package_path", "static/css/vizro-bootstrap.min.css"),
            (
                False,
                "external_url",
                f"https://cdn.jsdelivr.net/gh/mckinsey/vizro@{_git_branch}/vizro-core/src/vizro/static/css/vizro-bootstrap.min.css",
            ),
        ],
    )
    def test_css(self, serve_locally, resource_key, resource_value):
        app = vizro.Vizro(serve_locally=serve_locally)

        framework_css = app.dash.css.get_library_css("vizro")

        # Check same number of files
        assert len(framework_css) == len(set(VIZRO_ASSETS_PATH.rglob("*.css")))
        # Check vizro-bootstrap comes first and looks right
        assert framework_css[0] == {"namespace": "vizro", resource_key: resource_value}
        # Check rest is in alphabetical order
        assert framework_css[1:] == sorted(framework_css[1:], key=operator.itemgetter(resource_key))

    # Only external_url or relative_package_path will exist in the resource specification depending on
    # whether serve_locally=True (the Dash and Vizro default) or False.
    @pytest.mark.parametrize(
        "serve_locally, resource_key, resource_value",
        [
            (True, "relative_package_path", "static/js/models/time_picker.js"),
            (
                False,
                "external_url",
                f"https://cdn.jsdelivr.net/gh/mckinsey/vizro@{_git_branch}/vizro-core/src/vizro/static/js/models/time_picker.min.js",
            ),
        ],
    )
    def test_scripts(self, serve_locally, resource_key, resource_value):
        app = vizro.Vizro(serve_locally=serve_locally)

        framework_scripts = app.dash.scripts.get_library_scripts("vizro")

        # Check same number of files
        assert len(framework_scripts) == len(
            set(VIZRO_ASSETS_PATH.rglob("*.*")) - set(VIZRO_ASSETS_PATH.rglob("*.css"))
        )
        # Check a random file. It doesn't matter what this one is so long as it doesn't have dynamic=True, which would
        # make it impossible to check external_url.
        assert framework_scripts[-1] == {"namespace": "vizro", resource_key: resource_value}
        # Checking the order here is trickier because when dynamic=True some resources don't have external_url. The
        # order is less important than for CSS anyway, so we don't test it.

    def test_double_instantiation(self):
        # This wouldn't pass without the suppress(ValueError) around ComponentRegistry.registry.discard("vizro").
        vizro.Vizro()
        vizro.Vizro()


# Using Vizro as a library in a pure Dash app should include only resources stipulated in vizro._css_dist and
# vizro._js_dist and no other files from VIZRO_ASSETS_PATH.
class TestDashResources:
    @pytest.mark.parametrize("serve_locally, resource_key", [(True, "relative_package_path"), (False, "external_url")])
    def test_css(self, serve_locally, resource_key):
        app = dash.Dash(serve_locally=serve_locally)

        library_css = [{"namespace": "vizro", resource_key: resource[resource_key]} for resource in vizro._css_dist]
        assert app.css.get_library_css("vizro") == library_css

    # Only external_url or relative_package_path will exist in the resource specification depending on
    # whether serve_locally=True (the Dash and Vizro default) or False.
    @pytest.mark.parametrize("serve_locally, resource_key", [(True, "relative_package_path"), (False, "external_url")])
    def test_scripts(self, serve_locally, resource_key):
        app = dash.Dash(serve_locally=serve_locally)

        # The below would mirror test_vizro_css but we need to handle dynamic resources differently. These never have
        # external_url associated with them.
        # library_scripts =[{"namespace": "vizro", resource_key: resource[resource_key]} for resource in vizro._js_dist]
        library_scripts = []
        for resource in vizro._js_dist:
            if resource.get("dynamic", False):
                library_scripts.append(
                    {"namespace": "vizro", "dynamic": True, "relative_package_path": resource["relative_package_path"]}
                )
            else:
                library_scripts.append({"namespace": "vizro", resource_key: resource[resource_key]})

        assert app.scripts.get_library_scripts("vizro") == library_scripts


class TestBootstrapDetection:
    """Test automatic Bootstrap CSS detection."""

    @pytest.mark.parametrize(
        "external_stylesheets, vizro_bootstrap_included",
        [
            # Bootstrap detected - vizro bootstrap should NOT be included
            # String URL
            (["https://cdn.jsdelivr.net/npm/bootstrap@5.3.6/dist/css/bootstrap.min.css"], False),
            # Dict with href key
            (
                [{"href": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.6/dist/css/bootstrap.min.css"}],
                False,
            ),
            # Multiple stylesheets
            (["https://fonts.googleapis.com/css", "https://example.com/bootstrap.css"], False),
            # Mixed
            (
                [
                    "https://codepen.io/bWffds.css",
                    {"href": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.6/dist/css/bootstrap.min.css"},
                ],
                False,
            ),
            # Case insensitive
            (["https://example.com/BOOTSTRAP-theme.css"], False),
            # Bootstrap NOT detected - vizro bootstrap should be included
            ([], True),
            (["https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap"], True),
            ([{"href": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap"}], True),
            ([{"src": "https://bootstrap.css"}], True),  # Wrong key in dict
        ],
    )
    def test_include_vizro_bootstrap(self, external_stylesheets, vizro_bootstrap_included):
        app = Vizro(external_stylesheets=external_stylesheets)
        framework_css = app.dash.css.get_library_css("vizro")

        has_vizro_bootstrap = any(
            "vizro-bootstrap.min.css" in resource.get("relative_package_path", "") for resource in framework_css
        )
        assert has_vizro_bootstrap is vizro_bootstrap_included


class TestActionLogDevtool:
    """Tests for the DevTools logs panel: the toggle button (devtool), the persistent-layout offcanvas and callbacks."""

    @pytest.fixture
    def simple_dashboard(self):
        return vm.Dashboard(pages=[vm.Page(title="Test", components=[vm.Button()])])

    def test_devtool_registers_only_button(self, simple_dashboard, mocker):
        # The offcanvas now lives in the persistent layout (added by _add_vizro_logs_offcanvas), so only the toggle
        # button is registered into the DevTools menu via hooks.devtool.
        mock_devtool = mocker.patch("vizro._vizro.hooks.devtool")
        Vizro().build(simple_dashboard)
        assert mock_devtool.call_count == 1
        registered_types = {call.kwargs["component_type"] for call in mock_devtool.call_args_list}
        assert registered_types == {"Button"}

    def test_offcanvas_added_to_layout_in_debug(self, simple_dashboard):
        Vizro().build(simple_dashboard)
        dash.get_app()._dev_tools.ui = True
        layout = _add_vizro_logs_offcanvas(html.Div(id="served-layout"))
        assert "vizro_logs_offcanvas" in str(layout)

    def test_offcanvas_not_added_to_layout_outside_debug(self, simple_dashboard):
        Vizro().build(simple_dashboard)
        dash.get_app()._dev_tools.ui = False
        original = html.Div(id="served-layout")
        layout = _add_vizro_logs_offcanvas(original)
        assert layout is original
        assert "vizro_logs_offcanvas" not in str(layout)

    def test_store_sync_clientside_callback_registered(self, simple_dashboard):
        Vizro().build(simple_dashboard)
        clientside_callbacks = [
            cb for cb in dash._callback.GLOBAL_CALLBACK_LIST if cb.get("clientside_function") is not None
        ]
        outputs = [cb["output"] for cb in clientside_callbacks]
        assert any("vizro_logs.children" in output for output in outputs)

    def test_vizro_logs_store_in_page_layout(self, simple_dashboard):
        Vizro().build(simple_dashboard)
        page_layout = dash.page_registry[simple_dashboard.pages[0].id]["layout"]()
        assert "vizro_logs_store" in str(page_layout)


class TestRun:
    def test_run_block_with_undefined_captured_callables(self):
        dashboard_config = {
            "title": "Test dashboard",
            "pages": [
                {
                    "title": "Page 1",
                    "components": [
                        {
                            "type": "ag_grid",
                            "figure": {"_target_": "llm_generated_grid", "data_frame": "iris"},
                        },
                    ],
                }
            ],
        }
        dashboard = vm.Dashboard.model_validate(
            dashboard_config,
            context={"allow_undefined_captured_callable": ["llm_generated_grid"]},
        )
        app = Vizro().build(dashboard)
        with pytest.raises(ValueError, match="Dashboard contains models with undefined CapturedCallable's"):
            app.run()
