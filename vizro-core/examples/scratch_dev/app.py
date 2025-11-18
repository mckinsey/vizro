"""Dev app to try things out."""

from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm
from vizro.tables import dash_ag_grid

gapminder = px.data.gapminder()
gapminder_2007 = px.data.gapminder().query("year == 2007")
page = vm.Page(
    title="AG Grid",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(data_frame=gapminder_2007, dashGridOptions={"pagination": True}),
            title="Gapminder Data Insights",
            header="""#### An Interactive Exploration of Global Health, Wealth, and Population""",
            footer="""SOURCE: **Plotly gapminder data set, 2024**""",
        ),
        # vm.Card(text="Placeholder")
    ],
    # layout=vm.Flex()
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
