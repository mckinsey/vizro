import pandas as pd

from .build import DashboardBuilder
from .plan import get_dashboard_plan, print_dashboard_plan
from vizro.managers._data_manager import DataManager


class VizroAIDashboard:
    def __init__(self, model):
        self.model = model
        self.dashboard_plan = None

    def build_dashboard(self, df: pd.DataFrame, query: str, data_manager: DataManager, cleaned_df_names: list):
        first_df_name = cleaned_df_names[0]
        self.dashboard_plan = get_dashboard_plan(query, self.model, data_manager, cleaned_df_names)
        print_dashboard_plan(self.dashboard_plan)
        dashboard = DashboardBuilder(
            model=self.model,
            data=first_df_name,
            dashboard_plan=self.dashboard_plan,
            data_manager=data_manager,
        ).dashboard
        return dashboard
