import e2e.vizro.constants as cnst
from custom_charts.bar_custom import bar_with_highlight

import vizro.models as vm
import vizro.plotly.express as px

stocks = px.data.stocks()

datepicker_parameters_page = vm.Page(
    title=cnst.DATEPICKER_PARAMS_PAGE,
    components=[
        vm.Graph(
            id=cnst.BAR_CUSTOM_ID,
            figure=bar_with_highlight(
                x="date",
                data_frame=stocks,
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[f"{cnst.BAR_CUSTOM_ID}.highlight_bar"],
            selector=vm.DatePicker(
                id=cnst.DATEPICKER_PARAMS_ID,
                min="2018-01-01",
                max="2023-01-01",
                value="2018-04-01",
                range=False,
            ),
        ),
    ],
)
