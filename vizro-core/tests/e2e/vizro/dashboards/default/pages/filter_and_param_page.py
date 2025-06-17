import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px

iris = px.data.iris()

filter_and_param_page = vm.Page(
    title=cnst.FILTER_AND_PARAM_PAGE,
    components=[
        vm.Graph(
            id=cnst.BOX_FILTER_AND_PARAM_ID,
            figure=px.box(
                iris,
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(id=cnst.DROPDOWN_FILTER_AND_PARAM)),
        vm.Parameter(
            targets=[f"{cnst.BOX_FILTER_AND_PARAM_ID}.title"],
            selector=vm.RadioItems(id=cnst.RADIO_ITEMS_FILTER_AND_PARAM, options=["red", "blue"], value="blue"),
        ),
    ],
)
