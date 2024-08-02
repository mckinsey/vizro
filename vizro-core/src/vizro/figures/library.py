"""Contains unwrapped KPI card functions (suitable to use in pure Dash app)."""

from vizro.figures import kpi_card, kpi_card_reference

kpi_card = kpi_card.__wrapped__
kpi_card_reference = kpi_card_reference.__wrapped__


def f(a):
    """Blah blahblah"""
    pass


__all__ = ["kpi_card", "kpi_card_reference", "f"]
