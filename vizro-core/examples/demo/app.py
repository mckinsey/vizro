"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()

page = vm.Page(
    title="My first page",
    components=[vm.Graph(figure=px.bar(data_frame=gapminder.query("country == 'Germany'"), x="year", y="pop"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()

if __name__ == "__main__":
    Vizro().build(dashboard).run()
