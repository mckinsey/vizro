"""This is a test app to test the dashboard layout."""

from vizro import Vizro
import vizro.models as vm


import pandas as pd
import numpy as np
from vizro.tables import dash_ag_grid

# Sample data
data = {
    "user_id": range(1, 11),
    "name": ["Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace", "Hannah", "Ian", "Jane"],
    "age": np.random.randint(20, 50, size=10),
    "signup_date": pd.date_range(start="2023-01-01", periods=10, freq="W"),
    "active": np.random.choice([True, False], size=10),
}


df = pd.DataFrame(data)


page = vm.Page(
    title="Test page",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
    controls=[
        vm.Filter(
            column="active",
            selector=vm.Switch(
                value=False,
                label="Show active accounts",
                title="Switch selector title",
                description="This is a description for the new switch selector",
            ),
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
