import e2e.vizro.constants as cnst
from e2e.vizro.waiters import graph_load_waiter


def test_modebar(dash_br):
    """Check that modebar element exist for the chart."""
    dash_br.multiple_click(f"a[href='{cnst.FILTERS_PAGE_PATH}']", 1)
    dash_br.wait_for_element(f"#{cnst.SCATTER_GRAPH_ID} .modebar-container div[id^='modebar']")


def test_modebar_false(dash_br):
    """Check that modebar element disabled for the chart."""
    dash_br.multiple_click(f"a[href='{cnst.FILTERS_PAGE_PATH}']", 1)
    graph_load_waiter(dash_br, cnst.BOX_GRAPH_ID)
    dash_br.wait_for_no_elements(f'div[id="{cnst.BOX_GRAPH_ID}"] .modebar-container div[id^="modebar"]')
