"""Page plan model."""

import logging
from typing import List, Union

try:
    from pydantic.v1 import BaseModel, Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, PrivateAttr, validator
import vizro.models as vm
from tqdm.auto import tqdm
from vizro_ai.dashboard.response_models.components import ComponentPlan
from vizro_ai.dashboard.response_models.controls import ControlPlan
from vizro_ai.dashboard.response_models.layout import LayoutPlan
from vizro_ai.dashboard.utils import _execute_step

logger = logging.getLogger(__name__)


class PagePlanner(BaseModel):
    """Page plan model."""

    title: str = Field(
        ...,
        description="Title of the page. If no description is provided, "
        "make a short and concise title from the components.",
    )
    components_plan: List[ComponentPlan] = Field(
        ..., description="List of components. Must contain at least one component."
    )
    controls_plan: List[ControlPlan] = Field([], description="Controls of the page.")
    layout_plan: LayoutPlan = Field(None, description="Layout of the page.")

    _components: List[Union[vm.Card, vm.AgGrid, vm.Figure]] = PrivateAttr()
    _controls: List[vm.Filter] = PrivateAttr()
    _layout: vm.Layout = PrivateAttr()

    @validator("components_plan")
    def _check_components_plan(cls, v):
        if len(v) == 0:
            raise ValueError("A page must contain at least one component.")
        return v

    def __init__(self, **data):
        """Initialize the page plan."""
        super().__init__(**data)
        self._components = None
        self._controls = None
        self._layout = None

    def _get_components(self, df_metadata, model):
        if self._components is None:
            self._components = self._build_components(df_metadata, model)
        return self._components

    def _build_components(self, df_metadata, model):
        components = []
        component_log = tqdm(total=0, bar_format="{desc}", leave=False)
        with tqdm(
            total=len(self.components_plan),
            desc=f"Currently Building ... [Page] <{self.title}> components",
            leave=False,
        ) as pbar:
            for component_plan in self.components_plan:
                component_log.set_description_str(f"[Page] <{self.title}>: [Component] {component_plan.component_id}")
                pbar.update(1)
                components.append(component_plan.create(df_metadata=df_metadata, model=model))
        component_log.close()
        return components

    def _get_layout(self, model):
        if self._layout is None:
            self._layout = self._build_layout(model)
        return self._layout

    def _build_layout(self, model):
        if self.layout_plan is None:
            return None
        return self.layout_plan.create(model=model)

    def _get_controls(self, df_metadata, model):
        if self._controls is None:
            self._controls = self._build_controls(df_metadata, model)
        return self._controls

    def _available_components(self, df_metadata, model):
        return [
            comp.id
            for comp in self._get_components(df_metadata=df_metadata, model=model)
            if isinstance(comp, (vm.Graph, vm.AgGrid))
        ]

    def _build_controls(self, df_metadata, model):
        controls = []
        with tqdm(
            total=len(self.controls_plan),
            desc=f"Currently Building ... [Page] <{self.title}> controls",
            leave=False,
        ) as pbar:
            for control_plan in self.controls_plan:
                pbar.update(1)
                control = control_plan.create(
                    model=model,
                    available_components=self._available_components(df_metadata, model),
                    df_metadata=df_metadata,
                )
                if control:
                    controls.append(control)

        return controls

    def create(self, model, df_metadata):
        """Create the page."""
        page_desc = f"Building page: {self.title}"
        logger.info(page_desc)
        pbar = tqdm(total=5, desc=page_desc)

        title = _execute_step(pbar, page_desc + " --> add title", self.title)
        components = _execute_step(
            pbar, page_desc + " --> add components", self._get_components(df_metadata=df_metadata, model=model)
        )
        controls = _execute_step(pbar, page_desc + " --> add controls", self._get_controls(df_metadata, model))
        layout = _execute_step(pbar, page_desc + " --> add layout", self._get_layout(model))

        page = vm.Page(title=title, components=components, controls=controls, layout=layout)
        _execute_step(pbar, page_desc + " --> done", None)
        pbar.close()
        return page
