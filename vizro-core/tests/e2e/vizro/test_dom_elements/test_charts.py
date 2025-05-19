import e2e.vizro.constants as cnst


def test_modebar(dash_br):
    """Check that modebar element exist for the chart."""
    dash_br.multiple_click(f"a[href='{cnst.FILTERS_PAGE_PATH}']", 1)
    dash_br.wait_for_element(".modebar-container")
