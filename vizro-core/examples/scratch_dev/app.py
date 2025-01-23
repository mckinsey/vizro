"""Dev app to try things out."""

from vizro import Vizro
import vizro.models as vm
import vizro.plotly.express as px

from vizro.tables import dash_data_table

gapminder = px.data.gapminder()

page = vm.Page(
    title="Page",
    components=[
        vm.Table(
            figure=dash_data_table(data_frame=gapminder),
            title="Gapminder Data Insights",
        )
    ],
    controls=[
        vm.Filter(column="continent", selector=vm.Dropdown(value=["Europe"])),
        vm.Filter(column="continent", selector=vm.Dropdown(value="Europe", multi=False)),
        vm.Filter(column="continent", selector=vm.Checklist()),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
