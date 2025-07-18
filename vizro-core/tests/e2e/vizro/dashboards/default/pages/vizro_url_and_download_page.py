import e2e.vizro.constants as cnst
from dash import dcc

import vizro.models as vm
import vizro.plotly.express as px
from vizro.models.types import capture

iris = px.data.iris()


@capture("action")
def my_custom_export():
    return dcc.send_data_frame(iris.to_csv, cnst.VIZRO_DOWNLOAD_FILE)


@capture("action")
def my_custom_location():
    return f"/{cnst.DATEPICKER_PAGE}"


vizro_url_and_download_page = vm.Page(
    title=cnst.VIZRO_URL_AND_DOWNLOAD_PAGE,
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
                ),
                vm.Button(
                    id=cnst.BUTTON_VIZRO_DOWNLOAD,
                    text="Export data!",
                    actions=[
                        vm.Action(
                            function=my_custom_export(),
                            outputs=["vizro_download.data"],
                        )
                    ],
                ),
                vm.Button(
                    id=cnst.BUTTON_VIZRO_DOWNLOAD_COPY,
                    text="Copy Export data!",
                    actions=[
                        vm.Action(
                            function=my_custom_export(),
                            outputs=["vizro_download.data"],
                        )
                    ],
                ),
                vm.Button(
                    id=cnst.BUTTON_VIZRO_URL,
                    text=f"Go to {cnst.DATEPICKER_PAGE}!",
                    actions=[
                        vm.Action(
                            function=my_custom_location(),
                            outputs=["vizro_url.href"],
                        )
                    ],
                ),
                vm.Button(
                    id=cnst.BUTTON_VIZRO_URL_COPY,
                    text=f"Copy Go {cnst.DATEPICKER_PAGE}!",
                    actions=[
                        vm.Action(
                            function=my_custom_location(),
                            outputs=["vizro_url.href"],
                        )
                    ],
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
        )
    ],
)
