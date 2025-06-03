"""Global filter/parameters over vm.Tabs.

1. Create a single page app with one vm.Container and vm.Tabs.
2. Add a global CustomParameter with a vm.Slider to the collapsible vm.Container at the top of the page.
3. Add two vm.Containers with vm.Graph components within the vm.Tabs.
4. Graphs should use data from the data_manager that's modified with the vm.Parameter.
"""

from flask_caching import Cache

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.managers import data_manager
from vizro.models.types import capture
from vizro.models._controls._controls_utils import set_container_control_default


from typing import Literal, Optional, Any, Union


# TODO-Comment: Consider using parametrised data loading function so that only the needed data is loaded into the app.
# TODO-Docs: https://vizro.readthedocs.io/en/stable/pages/user-guides/data/#parametrize-data-loading
def load_data_function(number_of_data_points: int = 50):
    return px.data.iris().head(number_of_data_points)


# TODO-Comment: Consider setting up a data manager cache (PS: data is cached per function input argument)
# TODO-Docs: https://vizro.readthedocs.io/en/stable/pages/user-guides/data/#configure-cache
# data_manager.cache = Cache(config={
#     "CACHE_TYPE": "FileSystemCache",
#     "CACHE_DIR": "cache",
#     "CACHE_DEFAULT_TIMEOUT": 600,
# })

data_manager["data_key"] = load_data_function
# TODO-Comment: Consider adding timeout per dataset
# data_manager["data_key"].timeout = 300


# TODO-Comment:The following custom component is used to overcome the Vizro exception when targeting figures
#  outside its vm.Container.
# TODO-Docs: https://vizro.readthedocs.io/en/stable/pages/user-guides/custom-components/
class CustomParameter(vm.Parameter):
    """Custom Parameter used to overcome Vizro exception when targeting figures outside its vm.Container."""

    type: Literal["custom_parameter"] = "custom_parameter"

    def pre_build(self):
        set_container_control_default(control=self)
        self._check_numerical_and_temporal_selectors_values()
        self._check_categorical_selectors_options()
        self._set_selector_title()
        self._set_actions()


# TODO-Comment: The following line is needed to enable using CustomParameter in the Container components.
vm.Container.add_type("components", CustomParameter)


page_main = vm.Page(
    title="Main Page",
    description="""Single page app description.""",
    layout=vm.Flex(),
    components=[
        vm.Container(
            title="Global parameters and filters",
            description="Set global parameters and filters that apply to all tabs.",
            collapsed=False,
            components=[
                CustomParameter(
                    targets=[
                        "page_1_graph_1.data_frame.number_of_data_points",
                        "page_2_graph_1.data_frame.number_of_data_points"
                    ],
                    selector=vm.Slider(min=1, max=150, value=50)
                ),
            ],
            controls=[]
        ),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Page 1 title",
                    components=[
                        vm.Graph(
                            id="page_1_graph_1",
                            figure=px.scatter("data_key", x="sepal_length", y="petal_width", color="species"),
                        ),
                    ],
                    controls=[
                        vm.Filter(column="petal_length"),
                    ]
                ),
                vm.Container(
                    title="Page 2 title",
                    components=[
                        vm.Graph(
                            id="page_2_graph_1",
                            figure=px.scatter("data_key", x="sepal_length", y="petal_width", color="species"),
                        ),
                    ],
                    controls=[
                        vm.Filter(column="species", selector=vm.Checklist(title="Choose species")),
                    ]
                )
            ]
        )
    ]
)

dashboard = vm.Dashboard(pages=[page_main])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
