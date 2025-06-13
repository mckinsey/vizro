from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm
from vizro.tables import dash_ag_grid
from typing import Literal
from vizro.managers import data_manager
from vizro.models._controls._controls_utils import set_container_control_default


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


gapminder_2007 = px.data.gapminder().query("year == 2007")
tips = px.data.tips()
df = px.data.iris()


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

page1 = vm.Page(
    title="Tabs",
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
                        "page_2_graph_1.data_frame.number_of_data_points",
                    ],
                    selector=vm.Slider(min=1, max=150, value=50),
                ),
            ],
            controls=[],
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
                ),
                vm.Container(
                    title="Page 2 title",
                    components=[
                        vm.Graph(
                            id="page_2_graph_1",
                            figure=px.scatter(
                                "data_key", x="sepal_length", y="petal_width", color="species", height=600
                            ),
                        ),
                    ],
                ),
            ]
        ),
    ],
    controls=[
        vm.Filter(column="long_words"),
    ],
)


page2 = vm.Page(
    title="Tabs v2",
    layout=vm.Flex(),
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab1",
                    components=[
                        vm.Graph(
                            title="Graph 1",
                            figure=px.bar(
                                gapminder_2007,
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Tab2",
                    components=[
                        vm.Graph(
                            title="Graph 2",
                            figure=px.scatter(
                                gapminder_2007,
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Tab3",
                    layout=vm.Flex(),
                    components=[vm.Card(text="First card!"), vm.Card(text="Second card!"), vm.Card(text="Third card!")],
                ),
            ]
        )
    ],
)

page3 = vm.Page(
    title="Flex - default - graphs",
    layout=vm.Flex(),
    components=[vm.Graph(figure=px.violin(tips, y="tip", x="day", color="day", box=True)) for i in range(6)],
)


page4 = vm.Page(
    title="Tabs v3",
    # layout=vm.Flex(),
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab1",
                    layout=vm.Flex(direction="row"),
                    components=[
                        vm.Graph(
                            title="Graph 1",
                            figure=px.bar(gapminder_2007, x="continent", y="lifeExp", color="continent", height=400),
                        ),
                        vm.Card(text="Card 1"),
                    ],
                ),
                vm.Container(
                    title="Tab2",
                    components=[
                        vm.Graph(
                            title="Graph 2",
                            figure=px.scatter(
                                gapminder_2007,
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                    ],
                ),
            ]
        )
    ],
)


dashboard = vm.Dashboard(title="Test dashboard", pages=[page1, page2, page3, page4])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
