import e2e.vizro.constants as cnst
from custom_actions.custom_actions import scatter_click_data_custom_action

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import filter_interaction

iris = px.data.iris()


filter_interactions_page = vm.Page(
    title=cnst.FILTER_INTERACTIONS_PAGE,
    layout=vm.Grid(grid=[[0], [2], [1]]),
    components=[
        vm.Graph(
            id=cnst.SCATTER_INTERACTIONS_ID,
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
                custom_data=["species"],
            ),
            actions=[
                vm.Action(function=filter_interaction(targets=[cnst.BOX_INTERACTIONS_ID])),
                vm.Action(
                    function=scatter_click_data_custom_action(),
                    inputs=[f"{cnst.SCATTER_INTERACTIONS_ID}.clickData"],
                    outputs=[f"{cnst.CARD_INTERACTIONS_ID}"],
                ),
            ],
        ),
        vm.Card(id=cnst.CARD_INTERACTIONS_ID, text="### No data clicked."),
        vm.Graph(
            id=cnst.BOX_INTERACTIONS_ID,
            figure=px.box(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="species", targets=[cnst.BOX_INTERACTIONS_ID], selector=vm.Dropdown(id=cnst.DROPDOWN_INTER_FILTER)
        ),
        vm.Parameter(
            targets=[f"{cnst.BOX_INTERACTIONS_ID}.title"],
            selector=vm.RadioItems(id=cnst.RADIOITEM_INTER_PARAM, options=["red", "blue"], value="blue"),
        ),
    ],
)
