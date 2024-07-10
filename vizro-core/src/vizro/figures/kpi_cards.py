"""Contains undecorated KPI card functions (suitable to use in pure Dash app)."""

from vizro.models.types import capture

from .undecorated.kpi_cards import kpi_card, kpi_card_reference

kpi_card = capture("figure")(kpi_card)
kpi_card_reference = capture("figure")(kpi_card_reference)
