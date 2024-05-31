import pandas as pd
# from emoji import emojize
from .plan import print_dashboard_plan, get_dashboard_plan
from .build import DashboardBuilder

class VizroAIDashboard:
    def __init__(self, model):
        self.model = model
        # self.fig_builder = fig_builder
        self.dashboard_plan = None

    def build_dashboard(self, df: pd.DataFrame, query: str):
    #     print(emojize(
    # ":thinking_face::thinking_face::thinking_face: Trying to make sense of your gibberish.... :thinking_face::thinking_face::thinking_face: \n"))
        self.dashboard_plan = get_dashboard_plan(query, self.model)
    #     print(emojize(
    # ":light_bulb::light_bulb::light_bulb: I think I got you! Here is the plan.... :light_bulb::light_bulb::light_bulb: \n"))
        print_dashboard_plan(self.dashboard_plan)
    #     print(emojize(
    # ":hammer_and_wrench::hammer_and_wrench::hammer_and_wrench: Aye! Starting to build your nonsense... :hammer_and_wrench::hammer_and_wrench::hammer_and_wrench: \n"))
        dashboard = DashboardBuilder(
            model=self.model,
            data=df,
            dashboard_plan=self.dashboard_plan,
            # fig_builder=self.fig_builder
            ).dashboard
        return dashboard