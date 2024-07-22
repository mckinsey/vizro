import pytest
import vizro.plotly.express as px
from vizro_ai.dashboard.graph.code_generation import GraphState
from vizro_ai.dashboard.utils import DfMetadata


@pytest.fixture
def graph_state():
    state = GraphState(messages="", dfs=[px.data.medals_long()], df_metadata=DfMetadata(), pages=[])

    # dfs: List[pd.DataFrame]
    # df_metadata: DfMetadata
    # dashboard_plan: DashboardPlanner = None
    # pages: Annotated[List, operator.add]
    # dashboard: vm.Dashboard = None
