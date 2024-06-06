"""Module that contains the builder functionality."""

import vizro.models as vm
from tqdm.autonotebook import trange

from vizro_ai.utils.helper import DebugFailure


class PageBuilder:
    def __init__(self, model, data, page_plan):
        self._model = model
        self._data = data
        self._page_plan = page_plan
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
        for i in trange(
            len(self._page_plan.components.components), desc=f"Building components of page: {self._page_plan.title}"
        ):
            try:
                components.append(self._page_plan.components.components[i].create(data_frame=self._data, model=self._model))
            except DebugFailure as e:
                components.append(
                    vm.Card(
                        id=self._page_plan.components.components[i].component_id, text=f"Failed to build component: {e}"
                    )
                )
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
        for i in trange(
            len(self._page_plan.controls.controls), desc=f"Building controls of page: {self._page_plan.title}"
        ):
            controls.append(
                self._page_plan.controls.controls[i].create(
                    df=self._data, model=self._model, available_components=self.available_components
                )
            )
        return controls

    @property
    def page(self):
        if self._page is None:
            print(f"Building page: {self._page_plan.title}")
            print(f"Components: {self.components}")
            print(f"Controls: {self.controls}")
            self._page = vm.Page(title=self._page_plan.title, components=self.components, controls=self.controls)
        return self._page


class DashboardBuilder:
    def __init__(self, model, data, dashboard_plan):
        self._model = model
        self._data = data
        self._dashboard_plan = dashboard_plan
        self._pages = None

    @property
    def pages(self):
        if self._pages is None:
            self._pages = self._build_pages()
        return self._pages

    def _build_pages(self):
        pages = []
        for i in trange(len(self._dashboard_plan.pages), desc="Building pages"):
            pages.append(
                PageBuilder(
                    model=self._model,
                    data=self._data,
                    page_plan=self._dashboard_plan.pages[i],
                ).page
            )
        return pages

    @property
    def dashboard(self):
        return vm.Dashboard(title=self._dashboard_plan.title, pages=self.pages)
