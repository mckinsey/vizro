"""Flow charts."""

import vizro.models as vm

from pages._factories import waterfall_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file
from pages.examples import sankey

sankey_page = vm.Page(
    title="Sankey",
    path="flow/sankey",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
            #### What is a sankey chart?

            A Sankey chart is a type of flow diagram that illustrates how resources or values move between different
            stages or entities. The width of the arrows in the chart is proportional to the quantity of the flow,
            making it easy to see where the largest movements occur.

            &nbsp;

            #### When should I use it?

            Use a Sankey chart when you want to visualize the flow of resources, energy, money, or other values from
            one point to another. It is particularly useful for showing distributions and transfers within a system,
            such as energy usage, cost breakdowns, or material flows.

            Be mindful that Sankey charts can become cluttered if there are too many nodes or flows.
            To maintain clarity, focus on highlighting the most significant flows and keep the chart as simple as
            possible.
        """
        ),
        vm.Graph(figure=sankey.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("sankey.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("sankey.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

waterfall_page = waterfall_factory("flow")

pages = [sankey_page, waterfall_page]
