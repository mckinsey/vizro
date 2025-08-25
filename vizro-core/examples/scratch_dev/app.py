"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

df = px.data.gapminder()


page = vm.Page(
    id="page_1",
    title="Page 1",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
    # path="page_1",
)

page2 = vm.Page(
    id="page_2",
    title="Page 2",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
    # path="page_2",
)

page3 = vm.Page(
    id="page_3",
    title="Page 3",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
    # path="page_3",
)


dashboard = vm.Dashboard(
    pages=[page, page2, page3],
    navigation=vm.Navigation(
        # nav_selector=vm.NavBar(
        # pages=["page_1", "Page 2", "page_3"],
        # items=[
        #     vm.NavLink(label="Section 1", pages=["page_1", "page_2"]),
        #     vm.NavLink(label="Section 2", pages=["page_3"]),
        # ]
        # ),
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
