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
    # id="page_1",
    title="Page 1",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
)

page2 = vm.Page(
    # id="page_2",
    title="Page 2",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
)

page3 = vm.Page(
    # id="page_3",
    title="Page 3",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
)


dashboard = vm.Dashboard(
    pages=[page, page2, page3],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Section 1", pages=["Page 1", "Page 2"]),
                vm.NavLink(label="Section 2", pages=["Page 3"]),
            ]
        ),
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()

# Current behavior
# same title, no ids --> failure
# same title, ids --> success, sets as path the id
# home page is special, there the path is always empty
"""
How do we want it now:
- if user sets title, that's the path
- if duplicate title, then ID is the path
- duplicate ID is not allowed


So I think what we need as validation is the following:
- once we know what we are building, we can check if we have unique paths
- is it as simple as iterating through all pages paths?
- what cuold go wrong here: I set a duplicate title, but i set the id non-duplicate, so currently this would work
- the key mechanism is because currently the id is the same as the title, we can just take the id as path unless explicitly set and we basically have either title or id
- if we now do a simple cadence of path > title > id, then if someone sets a duplicate title not no id, then we would have a duplicate path...
- if we raise an error, then that is a breaking change, because before that would have worked, so we need something in the pre-build that modifies the path to the id in the case of a duplicate title


"""
