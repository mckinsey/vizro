from vizro import Vizro
import vizro.models as vm
from typing import Literal
from dash import html
import dash_bootstrap_components as dbc
from vizro.tables import dash_ag_grid
import vizro.plotly.express as px
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card
from vizro.tables import dash_ag_grid, dash_data_table

gapminder = px.data.gapminder()
iris = px.data.iris()
tips = px.data.tips()

# WORKS FINE - CAN BE ADDED TO STATIC CSS
page0 = vm.Page(
    title="Sticky headers - grid ",
    components=[
        vm.AgGrid(figure=dash_ag_grid(data_frame=gapminder)),
        vm.AgGrid(figure=dash_ag_grid(data_frame=iris)),
        vm.AgGrid(figure=dash_ag_grid(data_frame=tips)),
    ],
)

# WORKS FINE WITH CUSTOM CSS - CAN BE ADDED AS DOCS EXAMPLES WITH CAVEAT
page01 = vm.Page(
    title="Sticky headers - flex",
    layout=vm.Flex(),
    components=[
        vm.AgGrid(figure=dash_ag_grid(data_frame=gapminder), id="my-grid"),
        vm.Button(text="Button"),
    ],
)


# DOES NOT WORK AS TOO MANY AGGRIDS ARE ON ONE SCREEN WITH HEADERS THAT NEED TO BE
# POSITIONED DIFFERENTLY, SO MENTION THIS IN THE DOCS AS CAVEAT
page11 = vm.Page(
    title="Flex - default - aggrid",
    layout=vm.Flex(),
    components=[
        vm.AgGrid(figure=dash_ag_grid(tips)),
        vm.AgGrid(figure=dash_ag_grid(iris)),
        vm.AgGrid(figure=dash_ag_grid(gapminder)),
    ],
)


# THIS WORKS AGAIN, AS ALL HEADERS ARE ON THE SAME LEVEL - ADD TO DOCS
page13 = vm.Page(
    title="Flex - row - aggrid",
    layout=vm.Flex(direction="row"),
    components=[
        vm.AgGrid(figure=dash_ag_grid(tips)),
        vm.AgGrid(figure=dash_ag_grid(iris)),
        vm.AgGrid(figure=dash_ag_grid(gapminder)),
    ],
)


dashboard = vm.Dashboard(
    pages=[
        page0,
        page01,
        page11,
        page13,
    ],
    title="Test out Flex/Grid",
)


Vizro().build(dashboard).run()
