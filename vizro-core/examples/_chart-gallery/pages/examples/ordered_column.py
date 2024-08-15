import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()


page = vm.Page(
    title="Column",
    components=[
        vm.Graph(
            figure=px.bar(
                gapminder.query(
                    "year == 2007 and country.isin(['United States', 'Pakistan', 'India', 'China', 'Indonesia'])"
                ).sort_values("pop"),
                y="pop",
                x="country",
            )
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
