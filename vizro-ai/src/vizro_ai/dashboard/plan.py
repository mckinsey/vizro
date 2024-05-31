"""Module containing the planner functionality."""
from typing import Literal, List, Union, Optional
from pydantic.v1 import BaseModel as BaseModelV1
from pydantic.v1 import Field, validator, create_model
from .model import get_model

from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
import vizro.models as vm
from vizro.tables import dash_ag_grid
from vizro.models.types import SelectorType
from vizro.managers import model_manager
# from emoji import emojize

component_type = Literal["AgGrid", "Card", "Graph"]
control_type = Literal["Filter"]


class Component(BaseModelV1):
    component_name: component_type
    component_description: str = Field(...,
                                       description="Description of the component. Include everything that seems to relate to this component. If possible do not paraphrase and keep the original description. Keep any links as original links.")
    component_id: str = Field(pattern=r'^[a-z]+(_[a-z]+)?$',
                              description="Small snake case description of this component")

    def create(self, model, df):
        if self.component_name == "Graph":
            return vm.Graph()
            # return vm.Graph(id=self.component_id, figure=fig_builder.plot(df, self.component_description))
        elif self.component_name == "AgGrid":
            return vm.AgGrid(id=self.component_id, figure=dash_ag_grid(df))
        elif self.component_name == "Card":
            return get_model(self.component_description, model, result_model=vm.Card)


class Components(BaseModelV1):
    components: List[Component]


def create_filter_proxy(df, available_components):
    def validate_targets(v):
        if v not in available_components:
            raise ValueError(f"targets must be one of {available_components}")
        return v

    def validate_column(v):
        if v not in df.columns:
            raise ValueError(f"column must be one of {list(df.columns)}")
        return v

    # TODO: properly check this - e.g. what is the best way to ideally dynamically include the available components
    # even in the schema
    return create_model(
        'FilterProxy',
        column=(str, Field(..., description="The target column of the filter.")),
        targets=(
        List[str], Field([], description="The targets of the filter. Listen carefully to the instructions here.")),
        __validators__={
            "validator1": validator("targets", pre=True, each_item=True, allow_reuse=True)(validate_targets),
            "validator2": validator("column", allow_reuse=True)(validate_column)},
        __base__=vm.Filter,
    )


class Control(BaseModelV1):
    control_name: control_type
    control_description: str = Field(...,
                                     description="Description of the control. Include everything that seems to relate to this control.")

    # TODO: there is definitely room for dynamic model creation, e.g. with literals for targets
    def create(self, df, model, available_components):
        filter_prompt = (
            f"Create a filter from the following instructions: {self.control_description}. Do not make up "
            f"things that are optional and DO NOT configure actions, action triggers or action chains. If no options are specified, leave them out.")
        proxy = get_model(filter_prompt, model, result_model=create_filter_proxy(df, available_components))
        actual = vm.Filter.parse_obj(proxy.dict(exclude={'selector': {'id': True, 'actions':True}, 'id': True, 'type': True}))
        del model_manager._ModelManager__models[proxy.id] # TODO: This is very wrong and needs to change
        return actual


class Controls(BaseModelV1):
    controls: List[Control]


class PagePlanner(BaseModelV1):
    title: str = Field(...,
                       description="Title of the page. If no description is provided, make a short and concise title from the components.")
    components: Components  # List[Component]#
    controls: Controls  # Optional[List[FilterPlanner]]#List[Control]#


class DashboardPlanner(BaseModelV1):
    title: str = Field(...,
                       description="Title of the dashboard. If no description is provided, make a short and concise title from the content of the pages.")
    pages: List[PagePlanner]


def get_dashboard_plan(query: str, model: Union[ChatOpenAI],
                       max_retry: int = 3) -> PagePlanner:
    return get_model(query, model, result_model=DashboardPlanner, max_retry=max_retry)

def print_dashboard_plan(dashboard_plan):
    for i, page in enumerate(dashboard_plan.pages):
        # print(
        #     f"{emojize(':page_facing_up::page_facing_up:')} " + '\033[1m' + f" PAGE: {page.title} " + '\033[0m' + f"{emojize(':page_facing_up::page_facing_up:')} ")
        # print(emojize(':package::package::package::package:  COMPONENTS :package::package::package::package:',
        #               language='alias'))
        for j in page.components.components:
            print("--> "+repr(j))
        # available_components = [comp.component_id for comp in dashboard_plan.pages[0].components.components]
        # print(emojize(':control_knobs::control_knobs::control_knobs::control_knobs:  CONTROLS :control_knobs::control_knobs::control_knobs::control_knobs:',
        #               language='alias'))
        for j in page.controls.controls:
            print("--> "+repr(j))
        print("\n")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    # from vizro_ai import VizroAI
    from vizro import Vizro
    import plotly.express as px

    query = "I need a page with a bar chart shoing the population per continent "
    "and a scatter chart showing the life expectency per country as a function gdp. "
    "Make a filter on the GDP column and use a dropdown as selector. This filter should only "
    "apply to the bar chart. The bar chart should be a stacked bar chart, while "
    "the scatter chart should be colored by the column 'continent'. I also want "
    "a table that shows the data. The title of the page should be `My wonderful "
    "jolly dashboard showing a lot of data`."

    model = ChatOpenAI(model="gpt-4-turbo", temperature=0)

    # model = ChatAnthropic(
    #     model='claude-3-opus-20240229',
    #     anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
    #     anthropic_api_url=os.environ.get("ANTHROPIC_API_BASE")
    # )

    # fig_builder = VizroAI(model=model)
    gapminder = px.data.gapminder()

    plan = get_dashboard_plan(query, model)

    print_dashboard_plan(plan)
