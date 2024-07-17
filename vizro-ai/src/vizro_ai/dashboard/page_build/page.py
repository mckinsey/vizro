"""Module that contains the builder functionality."""

import logging

import vizro.models as vm
from tqdm.auto import tqdm
from vizro_ai.dashboard.utils import _execute_step
from vizro_ai.utils.helper import DebugFailure

logger = logging.getLogger(__name__)


class PageBuilder:
    """Class to build a page."""

    def __init__(self, model, df_metadata, page_plan):
        """Initialize PageBuilder."""
        self._model = model
        self._df_metadata = df_metadata
        self._page_plan = page_plan
        self._components = None
        self._controls = None
        self._page = None
        self._layout = None

    @property
    def components(self):
        """Property to get components."""
        if self._components is None:
            self._components = self._build_components()
        return self._components

    def _build_components(self):
        components = []
        component_log = tqdm(total=0, bar_format="{desc}", leave=False)
        with tqdm(
            total=len(self._page_plan.components_plan),
            desc=f"Currently Building ... [Page] <{self._page_plan.title}> components",
            leave=False,
        ) as pbar:
            for component_plan in self._page_plan.components_plan:
                component_log.set_description_str(
                    f"[Page] <{self._page_plan.title}>: [Component] {component_plan.component_id}"
                )
                pbar.update(1)
                try:
                    components.append(component_plan.create(df_metadata=self._df_metadata, model=self._model))
                except DebugFailure as e:
                    components.append(vm.Card(id=component_plan.component_id, text=f"Failed to build component: {e}"))
        component_log.close()
        return components

    @property
    def layout(self):
        """Property to get layout."""
        if self._layout is None:
            self._layout = self._build_layout()
        return self._layout

    def _build_layout(self):
        if self._page_plan.layout_plan is None:
            return None
        return self._page_plan.layout_plan.create(model=self._model)

    @property
    def controls(self):
        """Property to get controls."""
        if self._controls is None:
            self._controls = self._build_controls()
        return self._controls

    @property
    def available_components(self):
        """Property to get available components."""
        return [comp.id for comp in self.components if isinstance(comp, (vm.Graph, vm.AgGrid))]

    def _build_controls(self):
        controls = []
        with tqdm(
            total=len(self._page_plan.controls_plan),
            desc=f"Currently Building ... [Page] <{self._page_plan.title}> controls",
            leave=False,
        ) as pbar:
            for control_plan in self._page_plan.controls_plan:
                pbar.update(1)
            control = control_plan.create(
                model=self._model, available_components=self.available_components, df_metadata=self._df_metadata
            )
            if control:
                controls.append(control)

        return controls

    @property
    def page(self):
        """Property to get page."""
        if self._page is None:
            page_desc = f"Building page: {self._page_plan.title}"
            logger.info(page_desc)
            pbar = tqdm(total=5, desc=page_desc)

            title = _execute_step(pbar, page_desc + " --> add title", self._page_plan.title)
            components = _execute_step(pbar, page_desc + " --> add components", self.components)
            controls = _execute_step(pbar, page_desc + " --> add controls", self.controls)
            layout = _execute_step(pbar, page_desc + " --> add layout", self.layout)

            self._page = vm.Page(title=title, components=components, controls=controls, layout=layout)
            _execute_step(pbar, page_desc + " --> done", None)
            pbar.close()
        return self._page
