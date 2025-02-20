import operator

import dash
import pytest
from packaging.version import parse

import vizro
from vizro._constants import VIZRO_ASSETS_PATH

_git_branch = vizro.__version__ if not parse(vizro.__version__).is_devrelease else "main"


def test_vizro_bootstrap():
    assert (
        vizro.bootstrap
        == f"https://cdn.jsdelivr.net/gh/mckinsey/vizro@{_git_branch}/vizro-core/src/vizro/static/css/vizro-bootstrap.min.css"
    )


# Using Vizro as a framework should include both the library and framework resources i.e. all files in
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
            (True, "relative_package_path", "static/js/models/slider.js"),
            (
                False,
                "external_url",
                f"https://cdn.jsdelivr.net/gh/mckinsey/vizro@{_git_branch}/vizro-core/src/vizro/static/js/models/slider.min.js",
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
