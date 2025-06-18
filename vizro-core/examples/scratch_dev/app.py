import numpy as np

from vizro import Vizro
import vizro.models as vm
import pandas as pd
from vizro.tables import dash_ag_grid
import string


N = len(string.ascii_letters)
df = pd.DataFrame(
    {
        "category 1": np.random.choice(list("abc"), N),
        "category 2": np.random.choice(list("ABC"), N),
        "long_words": [" ".join(list(string.ascii_letters[: n + 1])) for n in range(N)],
        "numbers": np.random.randint(N, size=N),
    }
)


def dynamic_data(n=10):
    return df.loc[:n]


def make_controls():
    return [
        vm.Filter(column="long_words"),
        vm.Filter(
            column="category 1",
            selector=vm.Checklist(),
        ),
        vm.Filter(column="category 2", selector=vm.RadioItems()),
        vm.Filter(column="numbers"),
    ]


page_1 = vm.Page(
    title="Test page",
    components=[
        vm.Container(
            components=[vm.AgGrid(id="grid", figure=dash_ag_grid(dynamic_data))],
            controls=make_controls(),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["grid.data_frame.n"],
            selector=vm.Slider(
                title="Change me to see bug", min=0, max=N, step=1, marks={0: "0", N // 2: str(N // 2), N: str(N)}
            ),
        ),
        *make_controls(),
    ],
)

dashboard = vm.Dashboard(title="Test dashboard", pages=[page_1])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
