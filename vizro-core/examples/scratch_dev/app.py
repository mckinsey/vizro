# Vizro is an open-source toolkit for creating modular data visualization applications.
# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.models.types import capture
from vizro.figures import kpi_card
from vizro.actions import export_data

tips = px.data.tips()

first_page = vm.Page(
    title="Data",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(tips),
            footer="""**Data Source:** Bryant, P. G. and Smith, M. (1995).
            Practical Data Analysis: Case Studies in Business Statistics.
            Homewood, IL: Richard D. Irwin Publishing.""",
        ),
        vm.Button(text="Export Data", actions=[vm.Action(function=export_data())]),
    ],
)

dashboard = vm.Dashboard(pages=[first_page])
Vizro().build(dashboard).run()
if __name__ == "__main__":
    Vizro().build(dashboard).run()
