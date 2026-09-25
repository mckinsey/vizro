"""Built-in figure functions.

Abstract: Usage documentation
    [How to use figures](../user-guides/figure.md)
"""

from vizro.models.types import capture

from .library import kpi_card, kpi_card_reference, kpi_sparkline_card

__all__ = ["kpi_card", "kpi_card_reference", "kpi_sparkline_card"]

kpi_card = capture("figure")(kpi_card)
kpi_card_reference = capture("figure")(kpi_card_reference)
kpi_sparkline_card = capture("figure")(kpi_sparkline_card)
