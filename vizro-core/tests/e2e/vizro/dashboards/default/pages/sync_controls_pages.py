import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import set_controls

_df = px.data.iris()

sync_hidden_parameter_page = vm.Page(
    title=cnst.SYNC_HIDDEN_PARAMETER_PAGE,
    components=[
        vm.Graph(
            id=cnst.SYNC_HIDDEN_PARAMETER_GRAPH_ID,
            figure=px.scatter(_df, x="sepal_width", y="sepal_length", color="species"),
        )
    ],
    controls=[
        vm.Filter(
            id=cnst.SYNC_HIDDEN_PARAMETER_FILTER_ID,
            column="species",
            targets=[cnst.SYNC_HIDDEN_PARAMETER_GRAPH_ID, cnst.SYNC_HIDDEN_PARAMETER_PARAMETER_ID],
            selector=vm.RadioItems(id=cnst.SYNC_HIDDEN_PARAMETER_RADIO_ITEMS_ID),
        ),
        vm.Parameter(
            id=cnst.SYNC_HIDDEN_PARAMETER_PARAMETER_ID,
            targets=[f"{cnst.SYNC_HIDDEN_PARAMETER_GRAPH_ID}.title"],
            selector=vm.RadioItems(options=["setosa", "versicolor", "virginica"], value="setosa"),
            visible=False,
        ),
    ],
)

sync_cross_page_source_page = vm.Page(
    title=cnst.SYNC_CROSS_PAGE_SOURCE_PAGE,
    components=[
        vm.Graph(
            id=cnst.SYNC_CROSS_PAGE_SOURCE_GRAPH_ID,
            figure=px.scatter(_df, x="sepal_width", y="sepal_length", color="species"),
        ),
    ],
    controls=[
        vm.Filter(
            id=cnst.SYNC_CROSS_PAGE_SOURCE_FILTER_ID,
            column="species",
            targets=[cnst.SYNC_CROSS_PAGE_TARGET_FILTER_ID, cnst.SYNC_CROSS_PAGE_SOURCE_GRAPH_ID],
            selector=vm.RadioItems(
                id=cnst.SYNC_CROSS_PAGE_SOURCE_RADIO_ITEMS_ID,
                title="Species (syncs target page; no navigation)",
            ),
        ),
    ],
)

sync_cross_page_target_page = vm.Page(
    title=cnst.SYNC_CROSS_PAGE_TARGET_PAGE,
    components=[
        vm.Graph(
            id=cnst.SYNC_CROSS_PAGE_TARGET_GRAPH_ID,
            figure=px.scatter(_df, x="sepal_width", y="sepal_length", color="species"),
        ),
    ],
    controls=[
        vm.Filter(
            id=cnst.SYNC_CROSS_PAGE_TARGET_FILTER_ID,
            column="species",
            targets=[cnst.SYNC_CROSS_PAGE_TARGET_GRAPH_ID],
            selector=vm.Checklist(id=cnst.SYNC_CROSS_PAGE_TARGET_CHECKLIST_ID),
        ),
    ],
)

sync_drill_through_source_page = vm.Page(
    title=cnst.SYNC_DRILL_THROUGH_SOURCE_PAGE,
    components=[
        vm.Graph(
            id=cnst.SYNC_DRILL_THROUGH_SOURCE_GRAPH_ID,
            title="Click a point: sets this page's control live AND the target page's (applied on open); stays here",
            figure=px.scatter(_df, x="sepal_width", y="sepal_length", color="species", custom_data="species"),
            actions=set_controls(
                controls=[
                    cnst.SYNC_DRILL_THROUGH_SOURCE_FILTER_ID,
                    cnst.SYNC_DRILL_THROUGH_TARGET_FILTER_ID,
                ],
                value="species",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            id=cnst.SYNC_DRILL_THROUGH_SOURCE_FILTER_ID,
            column="species",
            targets=[cnst.SYNC_DRILL_THROUGH_SOURCE_GRAPH_ID],
            selector=vm.Dropdown(id=cnst.SYNC_DRILL_THROUGH_SOURCE_DROPDOWN_ID),
            show_in_url=True,
        ),
    ],
)

sync_drill_through_target_page = vm.Page(
    title=cnst.SYNC_DRILL_THROUGH_TARGET_PAGE,
    components=[
        vm.Graph(
            id=cnst.SYNC_DRILL_THROUGH_TARGET_GRAPH_ID,
            figure=px.scatter(_df, x="sepal_width", y="sepal_length", color="species"),
        ),
    ],
    controls=[
        vm.Filter(
            id=cnst.SYNC_DRILL_THROUGH_TARGET_FILTER_ID,
            column="species",
            targets=[cnst.SYNC_DRILL_THROUGH_TARGET_GRAPH_ID],
            selector=vm.RadioItems(id=cnst.SYNC_DRILL_THROUGH_TARGET_RADIO_ITEMS_ID),
            show_in_url=True,
        ),
    ],
)
