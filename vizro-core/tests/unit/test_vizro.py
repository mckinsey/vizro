import dash
import pytest

import vizro
from vizro._constants import VIZRO_ASSETS_PATH

_git_branch = vizro.__version__ if "dev" not in vizro.__version__ else "main"


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

        library_and_framework_css = app.dash.css.get_library_css("vizro")
        expected_library_css = [
            {"namespace": "vizro", resource_key: resource[resource_key]} for resource in vizro._css_dist
        ]

        # Check same number of files
        assert len(library_and_framework_css) == len(set(VIZRO_ASSETS_PATH.rglob("*.css")))
        # Check library css comes first
        assert library_and_framework_css[: len(expected_library_css)] == expected_library_css
        # Check vizro-bootstrap comes next and looks right
        assert library_and_framework_css[len(expected_library_css)] == {
            "namespace": "vizro",
            resource_key: resource_value,
        }
        # Check rest is in alphabetical order
        assert library_and_framework_css[len(expected_library_css) + 1 :] == sorted(
            library_and_framework_css[len(expected_library_css) + 1 :], key=lambda resource: resource[resource_key]
        )

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

        library_and_framework_scripts = app.dash.scripts.get_library_scripts("vizro")

        # The below would mirror test_vizro_css but we need to handle dynamic resources differently. These never have
        # external_url associated with them.
        # library_scripts = [{"namespace": "vizro", resource_key: resource[resource_key]}
        # for resource in vizro._js_dist]
        expected_library_scripts = []
        for resource in vizro._js_dist:
            if resource.get("dynamic", False):
                expected_library_scripts.append(
                    {"namespace": "vizro", "dynamic": True, "relative_package_path": resource["relative_package_path"]}
                )
            else:
                expected_library_scripts.append({"namespace": "vizro", resource_key: resource[resource_key]})

        # Check same number of files. Everything apart from css goes into scripts, not just js.
        assert len(library_and_framework_scripts) == len(
            set(VIZRO_ASSETS_PATH.rglob("*.*")) - set(VIZRO_ASSETS_PATH.rglob("*.css"))
        )
        # Check library scripts comes first
        assert library_and_framework_scripts[: len(expected_library_scripts)] == expected_library_scripts
        # Check last entry which is guaranteed to be a .js script rather than a dynamic asset that might not have
        # external_url.
        assert library_and_framework_scripts[-1] == {"namespace": "vizro", resource_key: resource_value}


# Using Vizro as a library in a pure Dash app should include only resources stipulated in vizro._css_dist and
# vizro._js_dist and no other files from VIZRO_ASSETS_PATH.
class TestDashResources:
    @pytest.mark.parametrize("serve_locally, resource_key", [(True, "relative_package_path"), (False, "external_url")])
    def test_css(self, serve_locally, resource_key):
        app = dash.Dash(serve_locally=serve_locally)

        expected_library_css = [
            {"namespace": "vizro", resource_key: resource[resource_key]} for resource in vizro._css_dist
        ]
        assert app.css.get_library_css("vizro") == expected_library_css

    # Only external_url or relative_package_path will exist in the resource specification depending on
    # whether serve_locally=True (the Dash and Vizro default) or False.
    @pytest.mark.parametrize("serve_locally, resource_key", [(True, "relative_package_path"), (False, "external_url")])
    def test_scripts(self, serve_locally, resource_key):
        app = dash.Dash(serve_locally=serve_locally)

        # The below would mirror test_vizro_css but we need to handle dynamic resources differently. These never have
        # external_url associated with them.
        # library_scripts = [{"namespace": "vizro", resource_key: resource[resource_key]}
        # for resource in vizro._js_dist]
        expected_library_scripts = []
        for resource in vizro._js_dist:
            if resource.get("dynamic", False):
                expected_library_scripts.append(
                    {"namespace": "vizro", "dynamic": True, "relative_package_path": resource["relative_package_path"]}
                )
            else:
                expected_library_scripts.append({"namespace": "vizro", resource_key: resource[resource_key]})

        assert app.scripts.get_library_scripts("vizro") == expected_library_scripts
