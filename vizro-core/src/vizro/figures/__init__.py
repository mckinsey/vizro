"""Built-in figure functions, typically aliased as `vf` using `import vizro.figures as vf`.

Abstract: Usage documentation
    [How to use figures](../user-guides/figure.md)
"""

from vizro.models.types import capture

from .library import kpi_card, kpi_card_reference

__all__ = ["kpi_card", "kpi_card_reference"]

kpi_card = capture("figure")(kpi_card)
kpi_card_reference = capture("figure")(kpi_card_reference)
