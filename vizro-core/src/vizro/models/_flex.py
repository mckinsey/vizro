import re
from typing import Annotated, Any, Literal

import dash_mantine_components as dmc
from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

from vizro._constants import GAP_DEFAULT
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call


class Flex(VizroBaseModel):
    """Flex layout for components on a [`Page`][vizro.models.Page] or in a [`Container`][vizro.models.Container].

    Abstract: Usage documentation
        [How to use the Flex layout](../user-guides/layouts.md#flex-layout)

    Args:
        direction (Literal["row", "column"]): Sets the direction of the flex items inside the container. Options are
            `row` or `column`. Defaults to `column`.
        gap (str): Specifies the gap between rows and columns. Allowed units: 'px', 'rem', 'em', or '%'.
            Defaults to `24px`.
        wrap (bool): Determines whether flex items are forced onto a single line or can wrap onto multiple lines.
            If `False`, all items will be on one line. If `True`, items will wrap onto multiple lines.
            Defaults to `False`.

    """

    type: Literal["flex"] = "flex"
    direction: Literal["row", "column"] = Field(
        default="column",
        description="Sets the direction of the flex items inside the container. Options are `row` or `column`."
        "Defaults to `column`.",
    )
    gap: str = Field(
        default=GAP_DEFAULT,
        description="Specifies the gap between rows and columns. Allowed units: 'px', 'rem', 'em', or '%'. "
        "Defaults to `24px`.",
        pattern=re.compile(r"^\d+(px|rem|em|%)$"),
    )
    wrap: bool = Field(
        default=False,
        description="Determines whether flex items are forced onto a single line or can wrap onto multiple lines. If "
        "`False`, all items will be on one line. If `True`, items will wrap onto multiple lines. Defaults to `False`.",
    )
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dmc.Flex` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dmc documentation](https://www.dash-mantine-components.com/components/flex)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    @_log_call
    def build(self):
        """Creates empty flex container to later position components in."""
        wrap_value = "wrap" if self.wrap else "nowrap"

        defaults = {
            "children": [],
            "gap": self.gap,
            "direction": self.direction,
            "wrap": wrap_value,
            "id": self.id,
        }

        return dmc.Flex(**(defaults | self.extra))
