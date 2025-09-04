import e2e.vizro.constants as cnst


def test_modebar(dash_br):
    """Check that modebar element exist for the chart."""
    dash_br.multiple_click(f"a[href='{cnst.FILTERS_PAGE_PATH}']", 1)
    dash_br.wait_for_element(f"#{cnst.SCATTER_GRAPH_ID} .modebar-container div[id^='modebar']")


def test_modebar_false(dash_br, check_graph_is_loaded_thread):
    """Check that modebar element disabled for the chart."""
    check_graph_is_loaded_thread(graph_id=cnst.BOX_GRAPH_ID)
    dash_br.multiple_click(f"a[href='{cnst.FILTERS_PAGE_PATH}']", 1)
    dash_br.wait_for_no_elements(f'div[id="{cnst.BOX_GRAPH_ID}"] .modebar-container div[id^="modebar"]')
