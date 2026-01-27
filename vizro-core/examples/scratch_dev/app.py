"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va

from vizro import Vizro
from vizro.models.types import capture
from vizro.tables import dash_ag_grid
import pandas as pd

df = px.data.iris()

data = {
    "user_id": range(1, 10),
    "name": ["Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace", "Hannah", "Ian"],
    "age": [10, 20, 30, 15, 25, 35, 25, 35, 45],
    "signup_date": [
        "2023-01-01",
        "2023-01-02",
        "2023-01-03",
        "2023-01-04",
        "2023-01-05",
        "2023-01-06",
        "2023-01-07",
        "2023-01-08",
        "2023-01-09",
    ],
    "active": [True, False, True, False, True, False, True, False, True],
}
df = pd.DataFrame(data)

page = vm.Page(
    title="Data",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
    controls=[
        vm.Filter(column="name", selector=vm.Checklist()),
    ],
)

dashboard = vm.Dashboard(pages=[page], title="Scratch Dev")
if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
