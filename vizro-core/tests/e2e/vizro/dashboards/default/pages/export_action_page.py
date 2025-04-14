import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import export_data

iris = px.data.iris()

export_action_page = vm.Page(
    title=cnst.EXPORT_PAGE,
    path=cnst.EXPORT_PAGE_PATH,
    layout=vm.Grid(grid=[[0], [1]]),
    components=[
        vm.Graph(
            id=cnst.LINE_EXPORT_ID,
            figure=px.line(
                iris,
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
        ),
        vm.Button(
            text="Export data",
            actions=[
                vm.Action(
                    function=export_data(
                        file_format="csv",
                    )
                ),
                vm.Action(
                    function=export_data(
                        file_format="xlsx",
                    )
                ),
            ],
        ),
    ],
)
