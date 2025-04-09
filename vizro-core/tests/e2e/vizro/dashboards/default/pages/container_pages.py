import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px

iris = px.data.iris()

container_variants_page = vm.Page(
    title=cnst.CONTAINER_VARIANTS_PAGE,
    components=[
        vm.Container(
            title="Container - filled",
            components=[
                vm.Graph(
                    id=cnst.SCATTER_FILLED, figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")
                )
            ],
            variant="filled",
        ),
        vm.Container(
            title="Container - outlined",
            components=[
                vm.Graph(
                    id=cnst.SCATTER_OUTLINED,
                    figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"),
                )
            ],
            variant="outlined",
        ),
    ],
)
