"""Dev app to try things out."""

from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm
from vizro.tables import dash_data_table

gapminder = px.data.gapminder()

table = vm.Page(
    title="Table",
    components=[
        vm.Table(
            figure=dash_data_table(data_frame=gapminde, page_size=5),
            title="Gapminder Data Insights",
            header="""#### An Interactive Exploration of Global Health, Wealth, and Population""",
            footer="""SOURCE: **Plotly gapminder data set, 2024**""",
        )
    ],
)


dashboard = vm.Dashboard(pages=[table])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
