"""Contains unwrapped KPI card functions (suitable to use in pure Dash app)."""

from vizro.figures import kpi_card, kpi_card_reference

kpi_card = kpi_card.__wrapped__
kpi_card_reference = kpi_card_reference.__wrapped__

__all__ = ["kpi_card", "kpi_card_reference"]
