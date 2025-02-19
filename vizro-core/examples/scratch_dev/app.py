"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.models.types import capture


df = px.data.iris()


@capture("ag_grid")
def my_custom_ag_grid(data_frame, chosen_columns, **kwargs):
    print(f"\nChosen column: {chosen_columns}\n")
    return dash_ag_grid(data_frame=data_frame[chosen_columns], **kwargs)()


page = vm.Page(
    title="Fix empty dropdown as parameter",
    layout=vm.Layout(grid=[[0, 1], [2, 2]]),
    components=[
        vm.Card(text="This is a test to fix the empty dropdown as parameter."),
        vm.Card(text="This is a test to fix the empty dropdown as parameter.", href="https://www.google.com"),
        vm.AgGrid(
            id="my_custom_ag_grid",
            figure=my_custom_ag_grid(
                data_frame=df,
                chosen_columns=df.columns.to_list(),
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["my_custom_ag_grid.chosen_columns"],
            selector=vm.Dropdown(
                title="Choose columns",
                options=df.columns.to_list(),
                multi=True,
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
