# Vizro is an open-source toolkit for creating modular data visualization applications.
# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

"""Example app from the official vizro user tutorial.

See: https://vizro.readthedocs.io/en/stable/pages/tutorials/explore-components/
"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card
from vizro.tables import dash_ag_grid, dash_data_table

tips = px.data.tips()


page1 = vm.Page(
    title="Grid - layout - aggrid",
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.AgGrid(figure=dash_ag_grid(tips)),
        vm.Graph(
            figure=px.violin(tips, y="tip", x="day", color="day", box=True),
        ),
    ],
)

page2 = vm.Page(
    title="Grid - default - aggrid",
    components=[
        vm.AgGrid(figure=dash_ag_grid(tips)),
        vm.Graph(
            figure=px.violin(tips, y="tip", x="day", color="day", box=True),
        ),
    ],
)

page3 = vm.Page(
    title="Flex - default - aggrid",
    layout=vm.Flex(),
    components=[vm.AgGrid(figure=dash_ag_grid(tips)) for i in range(3)],
)


page4 = vm.Page(
    title="Flex - gap - aggrid",
    layout=vm.Flex(gap="40px"),
    components=[vm.AgGrid(figure=dash_ag_grid(tips)) for i in range(3)],
)

page5 = vm.Page(
    title="Flex - row - aggrid",
    layout=vm.Flex(direction="row"),
    components=[vm.AgGrid(figure=dash_ag_grid(tips)) for i in range(3)],
)

page6 = vm.Page(
    title="Flex - default - table",
    layout=vm.Flex(),
    components=[vm.Table(figure=dash_data_table(tips)) for i in range(3)],
)


page7 = vm.Page(
    title="Flex - gap - table",
    layout=vm.Flex(gap="40px"),
    components=[vm.Table(figure=dash_data_table(tips)) for i in range(3)],
)

page8 = vm.Page(
    title="Flex - row - table",
    layout=vm.Flex(direction="row"),
    components=[vm.Table(figure=dash_data_table(tips)) for i in range(3)],
)

page9 = vm.Page(
    title="FlexItem - dimension - table",
    layout=vm.Flex(direction="row", wrap=True),
    components=[vm.Table(figure=dash_data_table(tips, style_table={"width": "1000px"})) for i in range(3)],
)

page10 = vm.Page(
    title="FlexItem - dimension - aggrid",
    layout=vm.Flex(direction="row", wrap=True),
    components=[vm.AgGrid(figure=dash_ag_grid(tips, style={"width": 1000})) for i in range(3)],
)

page11 = vm.Page(
    title="Flex - row - button",
    layout=vm.Flex(direction="row"),
    components=[vm.Button() for i in range(5)],
)


dashboard = vm.Dashboard(
    pages=[page1, page2, page3, page4, page5, page6, page7, page8, page9, page10, page11],
    title="Test out Flex/Grid",
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
