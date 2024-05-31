"""Module that contains the builder functionality."""
from tqdm.autonotebook import trange, tqdm
import vizro.models as vm
from vizro_ai.utils.helper import DebugFailure


class PageBuilder:
    def __init__(self, model, data, page_plan, fig_builder):
        self._model = model
        self._data = data
        self._page_plan = page_plan
        self._fig_builder = fig_builder
        self._components = None
        self._controls = None
        self._page = None

    @property
    def components(self):
        if self._components is None:
            self._components = self._build_components()
        return self._components

    def _build_components(self):
        components = []
        for i in trange(len(self._page_plan.components.components),
                        desc=f"Building components of page: {self._page_plan.title}"):
            try:
                components.append(
                    self._page_plan.components.components[i].create(fig_builder=self._fig_builder, df=self._data,
                                                                    model=self._model))
            except DebugFailure as e:
                components.append(vm.Card(id=self._page_plan.components.components[i].component_id,
                                          text=f"Failed to build component: {e}"))
        return components

    @property
    def controls(self):
        if self._controls is None:
            self._controls = self._build_controls()
        return self._controls

    @property
    def available_components(self):
        return [comp.id for comp in self.components if isinstance(comp, vm.Graph)]

    def _build_controls(self):
        controls = []
        for i in trange(len(self._page_plan.controls.controls),
                        desc=f"Building controls of page: {self._page_plan.title}"):
            controls.append(self._page_plan.controls.controls[i].create(df=self._data, model=self._model,
                                                                        available_components=self.available_components))
        return controls

    @property
    def page(self):
        if self._page is None:
            self._page = vm.Page(
                title=self._page_plan.title,
                components=self.components,
                controls=self.controls
            )
        return self._page


class DashboardBuilder:
    def __init__(self, model, data, dashboard_plan, fig_builder):
        self._model = model
        self._data = data
        self._dashboard_plan = dashboard_plan
        self._fig_builder = fig_builder
        self._pages = None

    @property
    def pages(self):
        if self._pages is None:
            self._pages = self._build_pages()
        return self._pages

    def _build_pages(self):
        pages = []
        for i in trange(len(self._dashboard_plan.pages), desc="Building pages"):
            pages.append(PageBuilder(model=self._model, data=self._data, page_plan=self._dashboard_plan.pages[i],
                                     fig_builder=self._fig_builder).page)
        return pages

    @property
    def dashboard(self):
        return vm.Dashboard(title=self._dashboard_plan.title, pages=self.pages)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    from vizro_ai import VizroAI
    from vizro import Vizro
    import plotly.express as px

    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    import vizro.models as vm
    from plan import get_dashboard_plan, print_dashboard_plan

    model = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    # model = ChatOpenAI(model="gpt-4-turbo", temperature=0)

    # model = ChatAnthropic(
    #     model='claude-3-opus-20240229',
    #     anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
    #     anthropic_api_url=os.environ.get("ANTHROPIC_API_BASE")
    # )
    fig_builder = VizroAI(model=model)

    df = px.data.gapminder()
    query = ("I need a page with a bar chart shoing the population per continent "
             "and a scatter chart showing the life expectency per country as a function gdp. "
             "Make a filter on the GDP column and use a dropdown as selector. This filter should only "
             "apply to the bar chart. The bar chart should be a stacked bar chart, while "
             "the scatter chart should be colored by the column 'continent'. I also want "
             "a table that shows the data. The title of the page should be: `This is big time data`. I also want a second page with just "
             "a card on it that links to `https://vizro.readthedocs.io/`. The title of the dashboard should be: `My wonderful "
             "jolly dashboard showing a lot of data`.")

    dashboard_plan = get_dashboard_plan(query, model)
    print_dashboard_plan(dashboard_plan)

    dashboard = DashboardBuilder(model=model, data=df, dashboard_plan=dashboard_plan, fig_builder=fig_builder).dashboard

    Vizro().build(dashboard).run()
