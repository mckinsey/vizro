"""Dev app to try things out."""

from vizro import Vizro
import vizro.models as vm
import vizro.plotly.express as px

stocks = px.data.stocks(datetimes=True)

page = vm.Page(
    title="Page",
    components=[
        vm.Graph(
            figure=px.line(stocks, x="date", y="GOOG", title="Stocks Data"),
        ),
    ],
    controls=[
        vm.Filter(column="GOOG"),
        vm.Filter(column="date", selector=vm.DatePicker(title="Date Picker (Stocks - date)")),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
