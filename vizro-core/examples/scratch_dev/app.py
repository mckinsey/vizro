"""This is a test app to test the dashboard layout."""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from typing import Literal
from dash import html
from vizro.models._dashboard import _all_hidden

df = px.data.iris()


class CustomDashboard(vm.Dashboard):
    """Custom Dashboard with different layout arrangement."""

    type: Literal["custom_dashboard"] = "custom_dashboard"

    def _arrange_page(self, outer_page):
        # The only thing that changes are line 25 and 27, where the children are differently assigned
        collapse_left_side = outer_page["collapse-left-side"]
        collapse_icon_outer = outer_page["collapse-icon-outer"]
        right_side = outer_page["right-side"]
        header = outer_page["header"]

        page_main = html.Div(id="page-main", children=[header, right_side])
        page_main_outer = html.Div(
            children=[collapse_left_side, collapse_icon_outer, page_main],
            className="page-main-outer no-left" if _all_hidden(collapse_icon_outer) else "page-main-outer",
        )
        return page_main_outer


page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
    ],
)


dashboard = CustomDashboard(pages=[page], title="Dashboard Title")

if __name__ == "__main__":
    Vizro().build(dashboard).run()
