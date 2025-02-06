def graph_load_waiter(driver, graph_id):
    """Waiting for graph's x-axis to appear."""
    driver.wait_for_element(f"div[id='{graph_id}'] path[class='xtick ticks crisp']")
