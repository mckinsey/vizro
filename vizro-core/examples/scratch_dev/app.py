"""Test app"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

page = vm.Page(
    title="New Line Height",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.Card(
            id="new-line-height",
            text="""
            # New

            ## What is Vizro?

            Vizro is an open-source dashboarding framework developed by McKinsey. Built with Plotly and Dash, Vizro
            provides a high-level API for creating interactive, production-ready dashboards with minimal code.
            It includes pre-configured layouts, themes, and components, making it easier to build data-driven
            applications.

            Even if you're not creating a Vizro app, you can still use its styling and design system in your Dash
            applications.

            ## Vizro Features Available for Dash Apps

            * Vizro Bootstrap-themed figure templates are available in the dash-bootstrap-templates library starting
            from version 2.1.0. Both dark and light-themed templates are included.

            * Vizro Bootstrap theme provides styling for Bootstrap components, allowing them to match the Vizro light
            or dark theme.

            * Vizro theme for other Dash components extends styling beyond Bootstrap. Vizro includes custom CSS to
            theme additional Dash components that are not part of Bootstrap. You can explore all the custom CSS files
            in their GitHub repository.

            * Vizro KPI cards like the ones shown in the image above can be added to a regular Dash app, bringing a
            visually consistent way to display key performance indicators. For more details, see this Plotly forum post.""",
        ),
        vm.Card(
            id="old-line-height",
            text="""
            # Old

            ## What is Vizro?

            Vizro is an open-source dashboarding framework developed by McKinsey. Built with Plotly and Dash, Vizro
            provides a high-level API for creating interactive, production-ready dashboards with minimal code.
            It includes pre-configured layouts, themes, and components, making it easier to build data-driven
            applications.

            Even if you're not creating a Vizro app, you can still use its styling and design system in your Dash
            applications.

            ## Vizro Features Available for Dash Apps

            * Vizro Bootstrap-themed figure templates are available in the dash-bootstrap-templates library starting
            from version 2.1.0. Both dark and light-themed templates are included.

            * Vizro Bootstrap theme provides styling for Bootstrap components, allowing them to match the Vizro light
            or dark theme.

            * Vizro theme for other Dash components extends styling beyond Bootstrap. Vizro includes custom CSS to
            theme additional Dash components that are not part of Bootstrap. You can explore all the custom CSS files
            in their GitHub repository.

            * Vizro KPI cards like the ones shown in the image above can be added to a regular Dash app, bringing a
            visually consistent way to display key performance indicators. For more details, see this Plotly forum post.""",
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
