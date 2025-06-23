"""Contains KPI card functions."""

from vizro.models.types import capture

from .library import kpi_card, kpi_card_reference

__all__ = ["kpi_card", "kpi_card_reference"]

kpi_card = capture("figure")(kpi_card)
kpi_card_reference = capture("figure")(kpi_card_reference)
