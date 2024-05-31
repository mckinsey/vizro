import pandas as pd
from .plan import print_dashboard_plan, get_dashboard_plan
from .build import DashboardBuilder

class VizroAIDashboard:
    def __init__(self, model):
        self.model = model
        self.dashboard_plan = None

    def build_dashboard(self, df: pd.DataFrame, query: str):
        self.dashboard_plan = get_dashboard_plan(query, self.model)
        print_dashboard_plan(self.dashboard_plan)
        dashboard = DashboardBuilder(
            model=self.model,
            data=df,
            dashboard_plan=self.dashboard_plan,
            ).dashboard
        return dashboard