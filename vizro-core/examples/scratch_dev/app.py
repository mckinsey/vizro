"""This is a test app to test the dashboard layout."""

import numpy as np
import pandas as pd
import vizro.models as vm
from vizro import Vizro
from vizro.tables import dash_ag_grid

# Sample data
data = {
    "user_id": range(1, 11),
    "name": ["Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace", "Hannah", "Ian", "Jane"],
    "age": np.random.randint(20, 50, size=10),
    "signup_date": pd.date_range(start="2023-01-01", periods=10, freq="W"),
    "active": np.random.choice([True, False], size=10),
    "active_numeric": np.random.choice([0, 1], size=10),
}


df = pd.DataFrame(data)


page = vm.Page(
    id="page_1",
    title="Page 1",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
    # path="page_1",
)

page2 = vm.Page(
    id="page_2",
    title="Page 2",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
    # path="page_2",
)

page3 = vm.Page(
    id="page_3",
    title="Page 3",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
    # path="page_3",
)


dashboard = vm.Dashboard(
    pages=[page, page2, page3],
    navigation=vm.Navigation(
        # nav_selector=vm.NavBar(
        # pages=["page_1", "Page 2", "page_3"],
        # items=[
        #     vm.NavLink(label="Section 1", pages=["page_1", "page_2"]),
        #     vm.NavLink(label="Section 2", pages=["page_3"]),
        # ]
        # ),
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
