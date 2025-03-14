import e2e.vizro.constants as cnst
from custom_components.dropdown import CustomDropdown
from custom_components.range_slider_non_cross import RangeSliderNonCross

import vizro.models as vm
import vizro.plotly.express as px

iris = px.data.iris()

custom_components_page = vm.Page(
    title=cnst.CUSTOM_COMPONENTS_PAGE,
    components=[
        vm.Graph(
            id=cnst.SCATTER_CUSTOM_COMPONENTS_ID,
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
        ),
        vm.Graph(
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            targets=[cnst.SCATTER_CUSTOM_COMPONENTS_ID],
            selector=CustomDropdown(
                id=cnst.CUSTOM_DROPDOWN_ID,
                options=["setosa", "versicolor", "virginica"],
            ),
        ),
        vm.Filter(
            column="sepal_length",
            targets=[cnst.SCATTER_CUSTOM_COMPONENTS_ID],
            selector=RangeSliderNonCross(id=cnst.CUSTOM_RANGE_SLIDER_ID, step=1.0),
        ),
    ],
)
