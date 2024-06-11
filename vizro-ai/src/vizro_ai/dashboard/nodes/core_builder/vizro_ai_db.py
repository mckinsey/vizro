from typing import Dict, List

from .build import DashboardBuilder
from .plan import get_dashboard_plan, print_dashboard_plan


class VizroAIDashboard:
    def __init__(self, model):
        self.model = model
        self.dashboard_plan = None

    def build_dashboard(self, query: str, df_metadata: Dict[str, Dict[str, str]]):
        self.dashboard_plan = get_dashboard_plan(query=query, model=self.model, df_metadata=df_metadata)
        print_dashboard_plan(self.dashboard_plan)
        dashboard = DashboardBuilder(
            model=self.model,
            df_metadata=df_metadata,
            dashboard_plan=self.dashboard_plan,
        ).dashboard
        return dashboard
