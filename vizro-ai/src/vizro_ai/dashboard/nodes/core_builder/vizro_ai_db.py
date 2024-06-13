from typing import Dict

from .build import DashboardBuilder
from .plan import _get_dashboard_plan, _print_dashboard_plan


class VizroAIDashboard:
    def __init__(self, model):
        self.model = model
        self.dashboard_plan = None

    def _build_dashboard(self, query: str, df_metadata: Dict[str, Dict[str, str]]):
        self.dashboard_plan = _get_dashboard_plan(query=query, model=self.model, df_metadata=df_metadata)
        _print_dashboard_plan(self.dashboard_plan)
        dashboard = DashboardBuilder(
            model=self.model,
            df_metadata=df_metadata,
            dashboard_plan=self.dashboard_plan,
        ).dashboard
        return dashboard
