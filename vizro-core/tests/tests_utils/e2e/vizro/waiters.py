from dash.testing.wait import until


def graph_load_waiter(driver, graph_id):
    """Waiting for graph's x-axis to appear."""
    driver.wait_for_element(f"div[id='{graph_id}'] path[class='xtick ticks crisp']")


def callbacks_finish_waiter(driver):
    until(driver._wait_for_callbacks, timeout=40, poll=0.3)
