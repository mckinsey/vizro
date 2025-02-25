from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Literal, Optional, cast

import dash_bootstrap_components as dbc
from dash import html
from pydantic import AfterValidator, BeforeValidator, Field, conlist
from pydantic.json_schema import SkipJsonSchema

from vizro.models import VizroBaseModel
from vizro.models._layout import set_layout
from vizro.models._models_utils import _log_call, check_captured_callable_model
from vizro.models.types import ComponentType

if TYPE_CHECKING:
    from vizro.models import Layout

# TODO[MS]: Remove or move comments in this file
# Ways to implement kwargs:
# 1. Use a dict[str, Any] that gets inserted as **kwargs into the dbc component
# 2. Use a dict[str, Any] that gets merged with the existing defaults, potentially spit out a warning if overlapping
# 3. Use a Pydantic model whose serialization gets merged with the existing defaults
# 4. Use some dynamic validation (see below) although I predict this to be ugly

# Still to check: how does a Skipped Json schema react with langchain and pydantic AI when used as result type?
# ---> Given the code in _convert_pydantic_to_openai_function, I think it would skip the schema!

# Extremely powerful, here and if not here, definitely in schema work: https://docs.pydantic.dev/latest/concepts/validation_decorator
# Also check: print(json.dumps(TypeAdapter(say_hello_to).json_schema(), indent=2))


# Further ideas:
# - could be a good idea to have pydantic model because we can "deprecate" and move over easily, we could then
# also use the extra for other experimental arguments not related to just the component
#

# Things to go through:
# - Discuss which method?
# - Discuss which models quickly
# - Discuss SkipJsonSchema and how we should announce it
# # add dbc in field description, make a central schema page


class Container(VizroBaseModel):
    """Container to group together a set of components on a page.

    Args:
        type (Literal["container"]): Defaults to `"container"`.
        components (list[ComponentType]): See [ComponentType][vizro.models.types.ComponentType]. At least one component
            has to be provided.
        title (str): Title to be displayed.
        layout (Optional[Layout]): Layout to place components in. Defaults to `None`.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.Container` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior if the defaults change.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and may
            not be supported in the future. Defaults to `{}`.

    """

    type: Literal["container"] = "container"
    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for components field
    components: conlist(  # type: ignore[valid-type]
        Annotated[ComponentType, BeforeValidator(check_captured_callable_model)],
        min_length=1,
    )
    title: str = Field(description="Title to be displayed.")
    layout: Annotated[Optional[Layout], AfterValidator(set_layout), Field(default=None, validate_default=True)]
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.Container` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior if the defaults change.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and may
            not be supported in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    @_log_call
    def build(self):
        # Title is not displayed if Container is inside Tabs using CSS combinators (only applies to outer container)
        # Other options we might want to consider in the future to hide the title:
        # 1) Argument inside Container.build that flags if used inside Tabs, then sets hidden attribute for the heading
        # or just doesn't supply the element at all
        # 2) Logic inside Tabs.build that sets hidden=True for the heading or uses del to remove the heading via
        # providing an ID to the heading and accessing it in the component tree
        # 3) New field in Container like short_title to allow tab label to be set independently
        from vizro.models import Layout

        self.layout = cast(
            Layout,  # cannot actually be None if you check components and layout field together
            self.layout,
        )
        components_container = self.layout.build()
        for component_idx, component in enumerate(self.components):
            components_container[f"{self.layout.id}_{component_idx}"].children = component.build()

        defaults = {
            "id": self.id,
            "children": [
                html.H3(children=self.title, className="container-title", id=f"{self.id}_title"),
                components_container,
            ],
            "fluid": True,
        }

        finals = defaults | self.extra
        return dbc.Container(**finals)
