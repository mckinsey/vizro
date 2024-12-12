"""Dev app to try things out."""

from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm
from typing import Literal
from dash import html, get_asset_url
import dash_bootstrap_components as dbc

# Create a custom component based on vm.Dashboard.
# See: https://vizro.readthedocs.io/en/stable/pages/user-guides/custom-components/#extend-an-existing-component
class CustomDashboard(vm.Dashboard):
    """Custom implementation of `Dashboard`."""

    type: Literal["custom_dashboard"] = "custom_dashboard"

    def _make_page_layout(self, *args, **kwargs):
        super_build_obj = super()._make_page_layout(*args, **kwargs)
        # We access the container with id="settings", where the theme switch is placed and add the H4.
        # You can see what's inside the settings.children container here: https://github.com/mckinsey/vizro/blob/main/vizro-core/src/vizro/models/_dashboard.py
        super_build_obj["settings"].children = [
            html.H4("Good morning, Li! ☕", style={"margin-bottom": "0"}),
            super_build_obj["settings"].children
        ]
        return super_build_obj


# Test app -----------------
page = vm.Page(
    title="Page Title",
    components=[vm.Graph(figure=px.box(px.data.iris(), x="species", y="petal_width", color="species"))],
    controls=[
        vm.Filter(column="species"),
        vm.Filter(column="sepal_length"),
    ],
)
dashboard = CustomDashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
