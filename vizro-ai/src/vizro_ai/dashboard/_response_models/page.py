"""Page plan model."""

import logging
import re
from collections import Counter
from typing import Annotated, Optional, Union

import vizro.models as vm
from pydantic import AfterValidator, BaseModel, Field, PrivateAttr, ValidationInfo
from tqdm.auto import tqdm

from vizro_ai.dashboard._response_models.components import ComponentPlan
from vizro_ai.dashboard._response_models.controls import ControlPlan
from vizro_ai.dashboard._response_models.layout import LayoutPlan
from vizro_ai.dashboard.utils import _execute_step

logger = logging.getLogger(__name__)


def _check_title(v):
    cleaned_title = re.sub(r"[^a-zA-Z0-9\s]", "", v)
    return cleaned_title


def _check_components_plan(v):
    if not v:
        raise ValueError("A page must contain at least one component.")
    return v


def _check_unsupported_specs(v, info: ValidationInfo):
    title = info.data.get("title", "Unknown Title")
    if v:
        logger.warning(f"\n ------- \n Unsupported specs on page <{title}>: \n {v}")
        return []


def _validate_component_id_unique(components_list):
    """Validate the component id is unique."""
    component_ids = [comp.component_id for comp in components_list]
    duplicates = [id for id, count in Counter(component_ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"Component ids must be unique. Duplicated component ids: {duplicates}")
    return components_list


class PagePlan(BaseModel):
    """Page plan model."""

    title: Annotated[
        str,
        AfterValidator(_check_title),
        Field(
            description="""
            Title of the page. If no description is provided,
            make a concise and descriptive title from the components.
            """,
        ),
    ]
    components_plan: Annotated[
        list[ComponentPlan],
        AfterValidator(_check_components_plan),
        AfterValidator(_validate_component_id_unique),
        Field(description="List of components. Must contain at least one component."),
    ]
    controls_plan: list[ControlPlan] = Field([], description="Controls of the page.")
    layout_plan: Optional[LayoutPlan] = Field(default=None, description="Layout of components on the page.")
    unsupported_specs: Annotated[
        list[str],
        AfterValidator(_check_unsupported_specs),
        Field(
            default=[],
            description="""
        List of unsupported specs. If there are any unsupported specs,
        list them here. If not, leave this as an empty list.
        """,
        ),
    ]

    _components: list[Union[vm.Card, vm.AgGrid, vm.Figure]] = PrivateAttr()
    _controls: list[vm.Filter] = PrivateAttr()
    _layout: vm.Layout = PrivateAttr()
    _components_code: dict = PrivateAttr()
    _components_imports: dict = PrivateAttr()

    def __init__(self, **data):
        """Initialize the page plan."""
        super().__init__(**data)
        self._components = None
        self._controls = None
        self._layout = None
        self._components_code = None
        self._components_imports = None

    # TODO: Add type hints on this page!
    def _get_components_and_code(self, model, all_df_metadata):
        if self._components is None:
            self._components, self._components_imports, self._components_code = self._build_components(
                model=model, all_df_metadata=all_df_metadata
            )
        return self._components, self._components_imports, self._components_code

    def _build_components(self, model, all_df_metadata):
        components = []
        components_code = []
        components_imports = []
        component_log = tqdm(total=0, bar_format="{desc}", leave=False)
        with tqdm(
            total=len(self.components_plan),
            desc=f"Currently Building ... [Page] <{self.title}> components",
            leave=False,
        ) as pbar:
            for component_plan in self.components_plan:
                component_log.set_description_str(f"[Page] <{self.title}>: [Component] {component_plan.component_id}")
                pbar.update(1)
                result = component_plan.create(model=model, all_df_metadata=all_df_metadata)
                component, imports, code = result.component, result.imports, result.code

                components.append(component)

                # Store the code for the component, currently this only applies to Graph component
                component_code = {}
                component_imports = {}
                if code:
                    component_code[component_plan.component_id] = code
                    components_code.append(component_code)
                    component_imports[component_plan.component_id] = imports
                    components_imports.append(component_imports)
        component_log.close()
        return components, components_imports, components_code

    def _get_layout(self, model, all_df_metadata):
        if self._layout is None:
            self._layout = self._build_layout(model, all_df_metadata)
        return self._layout

    def _build_layout(self, model, all_df_metadata):
        if self.layout_plan is None:
            return None
        return self.layout_plan.create(
            component_ids=self._get_component_ids(model=model, all_df_metadata=all_df_metadata),
        )

    def _get_controls(self, model, all_df_metadata):
        if self._controls is None:
            self._controls = self._build_controls(model=model, all_df_metadata=all_df_metadata)
        return self._controls

    def _controllable_components(self, model, all_df_metadata):
        return [
            comp.id
            # TODO: improve on taking element by position
            for comp in self._get_components_and_code(model=model, all_df_metadata=all_df_metadata)[0]
            if isinstance(comp, (vm.Graph, vm.AgGrid))
        ]

    def _get_component_ids(self, model, all_df_metadata):
        return [comp.id for comp in self._get_components_and_code(model=model, all_df_metadata=all_df_metadata)[0]]

    def _build_controls(self, model, all_df_metadata):
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
                    controllable_components=self._controllable_components(model=model, all_df_metadata=all_df_metadata),
                    all_df_metadata=all_df_metadata,
                )
                if control:
                    controls.append(control)

        return controls

    def create(self, model, all_df_metadata) -> tuple[Union[vm.Page, None], Optional[str], Optional[str]]:
        """Create the page."""
        page_desc = f"Building page: {self.title}"
        logger.info(page_desc)
        pbar = tqdm(total=5, desc=page_desc)

        title = _execute_step(pbar, page_desc + " --> add title", self.title)
        components, components_imports, components_code = _execute_step(
            pbar,
            page_desc + " --> add components",
            self._get_components_and_code(model=model, all_df_metadata=all_df_metadata),
        )
        controls = _execute_step(
            pbar, page_desc + " --> add controls", self._get_controls(model=model, all_df_metadata=all_df_metadata)
        )
        layout = _execute_step(
            pbar, page_desc + " --> add layout", self._get_layout(model=model, all_df_metadata=all_df_metadata)
        )

        try:
            page = vm.Page(title=title, components=components, controls=controls, layout=layout)
        except Exception as e:
            # TODO: This Exception might be redundant. Check if it can be removed.
            if any("Number of page and grid components need to be the same" in error["msg"] for error in e.errors()):
                logger.warning(
                    """
[FALLBACK] Number of page and grid components provided are not the same.
Build page without layout.
"""
                )
                page = vm.Page(title=title, components=components, controls=controls, layout=None)
            else:
                logger.warning(f"[FALLBACK] Failed to build page: {self.title}. Reason: {e}")
                page = None
        _execute_step(pbar, page_desc + " --> done", None)
        pbar.close()
        return page, components_imports, components_code


if __name__ == "__main__":
    import pandas as pd
    from dotenv import load_dotenv

    from vizro_ai._llm_models import _get_llm_model
    from vizro_ai.dashboard.utils import AllDfMetadata, DfMetadata

    load_dotenv()

    model = _get_llm_model()

    all_df_metadata = AllDfMetadata(
        all_df_metadata={
            "gdp_chart": DfMetadata(
                df_schema={"a": "int64", "b": "int64"},
                df=pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}),
                df_sample=pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}),
            )
        }
    )
    page_plan = PagePlan(
        title="Worldwide GDP",
        components_plan=[
            ComponentPlan(
                component_type="Card",
                component_description="Create a card says 'this is worldwide GDP'.",
                component_id="gdp_card",
                df_name="N/A",
            )
        ],
        controls_plan=[
            ControlPlan(
                control_type="Filter",
                control_description="Create a filter that filters the data by column 'a'.",
                df_name="gdp_chart",
            )
        ],
        layout_plan=LayoutPlan(
            layout_grid_template_areas=[],
        ),
        unsupported_specs=[],
    )
    page = page_plan.create(model, all_df_metadata)
    print(page)  # noqa: T201
