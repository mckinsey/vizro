"""Example to show dashboard configuration."""
import random
from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm

date_date_frame = pd.DataFrame({
    "time": [datetime.datetime(2024, 1, 1) + datetime.timedelta(days=i) for i in range(31)],
    "value": [random.randint(0, 100) for _ in range(31)]
})

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(figure=px.scatter(date_date_frame, x="time", y="value")),
    ],
    controls=[
        vm.Filter(column="time"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
