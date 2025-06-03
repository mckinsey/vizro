"""Global filter/parameters.

1. Add main page with a global-slider.
2. Add dcc.Store component to the global dashboard level layout to store global-slider value.
3. Add action function to update the dcc.Store component with the value of the global-slider.
4. Add two pages with graphs that use data from the data_manager that's modified by the hidden Parameter.
5. Add hidden Parameter to each page that dynamically sets the data_manager data loading function arguments.
6. Add clientside callbacks to update the hidden Parameter values based on the dcc.Store component.
"""

from dash import clientside_callback, dcc, ClientsideFunction, Output, Input, State
from flask_caching import Cache

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.managers import data_manager
from vizro.models.types import capture

from typing import Literal, Optional, Any, Union


# TODO-Comment: Consider using parametrised data loading function so that only the needed data is loaded into the app.
# TODO-Docs: https://vizro.readthedocs.io/en/stable/pages/user-guides/data/#parametrize-data-loading
def load_data_function(number_of_data_points: int = 150):
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


# TODO-Comment: This is a Vizro action function triggered when the slider (from the "main_page") value changes.
# TODO-Docs: https://vizro.readthedocs.io/en/stable/pages/user-guides/actions/
@capture("action")
def update_dcc_store(slider_1, current_store):
    """Update the global parameters store with the value of the slider."""
    current_store["number_of_data_points"] = slider_1
    return current_store


# TODO-Comment: The following line is needed to enable using vm.Slider in the Page components.
vm.Page.add_type("components", vm.Slider)

page_main = vm.Page(
    title="Main Page",
    description="""Set global parameters and filters that apply to all pages.""",
    components=[
        vm.Slider(
            id="main_page_slider_1",
            title="Number of data points",
            min=1,
            max=150,
            value=50,
            actions=[
                # TODO-Comment: This action updates the dcc.Store component with the value of the slider.
                vm.Action(
                    function=update_dcc_store(),
                    inputs=[
                        "main_page_slider_1.value",
                        "global_parameters_store_id.data"  # This is the dcc.Store component
                    ],
                    outputs=["global_parameters_store_id.data"]
                )
            ]
        ),
    ]
)


# TODO-Comment: The following custom component is used to overcome the Dash DuplicateOutput exception.
# TODO-Docs: https://vizro.readthedocs.io/en/stable/pages/user-guides/custom-components/
class CustomSlider(vm.Slider):
    """Custom slider component used as a hidden Parameter selector. Used to overcome dash DuplicateOutput exception."""
    type: Literal["custom_slider"] = "custom_slider"

    def __call__(self, *args, **kwargs):
        defaults = {
            "id": self.id,
            "min": self.min,
            "max": self.max,
            "value": self.value,
        }

        return dcc.Slider(**defaults)


# TODO-Comment: The following line is needed to enable using CustomSlider as the Parameter selector.
vm.Parameter.add_type("selector", CustomSlider)

page_1 = vm.Page(
    title="Page 1",
    components=[
        vm.Graph(
            id="page_1_graph_1",
            figure=px.scatter("data_key", x="sepal_length", y="petal_width", color="species"),
        ),
    ],
    controls=[
        vm.Filter(
            column="petal_length",
            selector=vm.RangeSlider(
                title="Petal length",
                description="Filter the data by petal length.",
            )
        ),
        # TODO-Comment: This is hidden Parameter that reuses the global parameter from the main page.
        #  It can be hidden with the custom css like:
        #  ```css
        #  #page_1_hidden_global_parameter_1 {
        #      display: none;
        #  }
        #  ```
        # TODO-Docs: https://vizro.readthedocs.io/en/stable/pages/user-guides/custom-css/
        vm.Parameter(
            targets=["page_1_graph_1.data_frame.number_of_data_points"],
            selector=CustomSlider(
                id="page_1_hidden_global_parameter_1",
                min=1,
                max=150,
                value=50,
            )
        )
    ]
)

page_2 = vm.Page(
    title="Page 2",
    components=[
        vm.Graph(
            id="page_2_graph_1",
            figure=px.scatter("data_key", x="sepal_length", y="petal_width", color="species"),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Checklist(title="Choose species")),
        vm.Parameter(
            targets=["page_2_graph_1.data_frame.number_of_data_points"],
            selector=CustomSlider(
                id="page_2_hidden_global_parameter_1",
                min=1,
                max=150,
                value=50,
            )
        ),
    ]
)


# TODO-Comment: Here's an example of applying stored values from the "global_parameters_store_id" to the relevant and
#  hidden page "vm.Parameter". This is triggered when the "Page 1" is opened.
clientside_callback(
    ClientsideFunction(namespace="custom", function_name="update_hidden_parameters"),
    Output("page_1_hidden_global_parameter_1", "value"),
    # 'page_1_hidden_global_parameter_1 | id' is used as the callback Input which causes this callback to be triggered.
    Input("page_1_hidden_global_parameter_1", "id"),
    State("global_parameters_store_id", "data"),
)

# TODO-Comment: The same callback but for the "Page 2" hidden parameter.
clientside_callback(
    ClientsideFunction(namespace="custom", function_name="update_hidden_parameters"),
    Output("page_2_hidden_global_parameter_1", "value"),
    # 'page_2_hidden_global_parameter_1 | id' is used as the callback Input which causes this callback to be triggered.
    Input("page_2_hidden_global_parameter_1", "id"),
    State("global_parameters_store_id", "data"),
)

dashboard = vm.Dashboard(pages=[page_main, page_1, page_2])


if __name__ == "__main__":
    app = Vizro().build(dashboard)

    # TODO-Comment: Adding a dcc.Store component to the global dashboard level layout to store global parameters.
    app.dash.layout.children.append(
        dcc.Store(
            id="global_parameters_store_id",
            storage_type="session",
            data={"number_of_data_points": 50}  # Default value
        )
    )

    app.run()
