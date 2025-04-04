import re
from typing import Literal

from dash import html
from pydantic import Field

from vizro._constants import GAP_DEFAULT
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call


class Flex(VizroBaseModel):
    """Flex Container to place chart/components on the [`Page`][vizro.models.Page].

    Args:
        type (Literal["flex"]): Defaults to `"flex"`.
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

    @_log_call
    def build(self):
        """Creates empty flex container to later position components in."""
        bs_wrap = "flex-wrap" if self.wrap else "flex-nowrap"
        component_container = html.Div(
            [],
            style={"gap": self.gap},
            className=f"d-flex flex-{self.direction} {bs_wrap}",
            id=self.id,
        )
        return component_container
