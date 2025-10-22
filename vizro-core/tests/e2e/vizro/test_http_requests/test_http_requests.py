import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_http_requests_count
from playwright.sync_api import sync_playwright


def http_requests(func):
    """Decorator for setting up playwright logic."""

    def wrapper(request):
        with sync_playwright() as p:
            # selecting the Chromium browser engine which starts a new browser instance
            browser = p.chromium.launch()
            # creating browser context - clean, isolated browser profile
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            # creating a new page inside the context
            page = context.new_page()

            # Note: http_requests_paths keeps updating dynamically during the test.
            # This works because Python passes the list by reference, so both the decorator
            # and the test see the same list object in memory. Every new HTTP request triggers
            # the attached on_request listener, which appends to this shared list in real time.
            # The http_requests_paths is freshly created for each test run.
            http_requests_paths = []

            def on_request(request):
                if any(r in request.url for r in ["_dash-update-component"]):
                    http_requests_paths.append(request.url.split("/")[3])

            page.on("request", on_request)

            try:
                # open the page without chart (1 http)
                page.goto("http://127.0.0.1:5002/")
                check_http_requests_count(page, http_requests_paths, 1)

                # clear http requests list for the main test
                http_requests_paths.clear()

                # Call the actual test function, passing the Playwright `page` and the `http_requests_paths` list.
                # The list starts empty but is continuously updated by the attached `on_request` listener.
                func(page, http_requests_paths)

            except Exception:
                page.screenshot(path=f"{request.node.name}.png", full_page=True)
                raise

            finally:
                browser.close()

    return wrapper


@http_requests
def test_page_without_chart(page, http_requests_paths):
    # click on the button (1 http)
    page.locator(f"#{cnst.PAGE_WITHOUT_CHART}_button").click()
    check_http_requests_count(page, http_requests_paths, 1)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 1, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_page_with_one_chart(page, http_requests_paths):
    # open the page with one chart (2 http)
    page.locator(f"a[href='/{cnst.PAGE_WITH_ONE_CHART}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # delete one value from filter (1 http)
    page.get_by_text("×").nth(0).click()  # noqa RUF001
    check_http_requests_count(page, http_requests_paths, 3)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 3, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_explicit_actions_chain(page, http_requests_paths):
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.PAGE_EXPLICIT_ACIONS_CHAIN}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # click on the button - explicit actions chain (3 http)
    page.locator(f"#{cnst.PAGE_EXPLICIT_ACIONS_CHAIN}_button").click()
    check_http_requests_count(page, http_requests_paths, 5, sleep=3000)

    # select radio items filter value (1 http)
    page.get_by_text("Americas").nth(0).click()
    check_http_requests_count(page, http_requests_paths, 6)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 6, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_implicit_actions_chain(page, http_requests_paths):
    # open the page without chart (1 http)
    page.locator(f"a[href='/{cnst.PAGE_IMPLICIT_ACIONS_CHAIN}']").click()
    check_http_requests_count(page, http_requests_paths, 1)

    # click on the button - implicit actions chain (2 http)
    page.locator(f"#{cnst.PAGE_IMPLICIT_ACIONS_CHAIN}_button").click()
    check_http_requests_count(page, http_requests_paths, 3)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 3, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_chart_with_filter_interaction(page, http_requests_paths):
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.PAGE_CHART_WITH_FILTER_INTERACTION}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # filter interaction between charts (1 http)
    element = page.locator(".box").nth(1)
    box = element.bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    check_http_requests_count(page, http_requests_paths, 3)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 3, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_ag_grid_with_filter_interaction(page, http_requests_paths):
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.PAGE_AG_GRID_WITH_FILTER_INTERACTION}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # filter interaction between af grid and chart (1 http)
    page.get_by_role("gridcell", name="Europe").nth(0).click()
    check_http_requests_count(page, http_requests_paths, 3)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 3, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_dynamic_parametrisation(page, http_requests_paths):
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.PAGE_DYNAMIC_PARAMETRISATION}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # reload the page (2 http)
    page.reload(wait_until="networkidle")
    check_http_requests_count(page, http_requests_paths, 4)

    # select radio items data_frame_parameter value (1 http)
    page.get_by_text("Oceania").nth(0).click()
    check_http_requests_count(page, http_requests_paths, 5)

    # check that "Oceania" present in dropdown filter and select it (1 http)
    page.locator(".Select-arrow").click()
    page.locator('div[class="VirtualizedSelectOption"]').get_by_text("Oceania").click()
    check_http_requests_count(page, http_requests_paths, 6)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 6, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_all_selectors(page, http_requests_paths):
    """Page with all selectors present."""
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.PAGE_ALL_SELECTORS}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # reload the page (2 http)
    page.reload(wait_until="networkidle")
    check_http_requests_count(page, http_requests_paths, 4)

    # select radio items data_frame_parameter value (1 http)
    page.get_by_text("Oceania").nth(0).click()
    check_http_requests_count(page, http_requests_paths, 5)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 5, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_all_selectors_in_url(page, http_requests_paths):
    """Page with all selector present as url parameters."""
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.PAGE_ALL_SELECTORS_IN_URL}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # reload the page (2 http)
    page.reload(wait_until="networkidle")
    check_http_requests_count(page, http_requests_paths, 4)

    # select radio items data_frame_parameter value (1 http)
    page.get_by_text("Oceania").nth(0).click()
    check_http_requests_count(page, http_requests_paths, 5)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 5, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_set_control_cross_filter_graph(page, http_requests_paths):
    """Page with set_control action for graph working as cross filter."""
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.SET_CONTROL_GRAPH_CROSS_FILTER_PAGE}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # cross-filter between charts (2 http)
    # here we have 2 http requests because implicit actions chain happens
    # and set_control implicitly triggers the filter_action
    # https://vizro.readthedocs.io/en/stable/pages/tutorials/custom-actions-tutorial/#implicit-actions-chain
    element = page.locator('path[class="point plotly-customdata"]').nth(20)
    box = element.bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    check_http_requests_count(page, http_requests_paths, 4)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 4, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_set_control_cross_filter_ag_grid(page, http_requests_paths):
    """Page with set_control action for ag_grid working as cross filter."""
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.SET_CONTROL_TABLE_AG_GRID_CROSS_FILTER_PAGE}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # cross-filter between ag grid and chart (2 http)
    # here we have 2 http requests because implicit actions chain happens
    # and set_control implicitly triggers the filter_action
    # https://vizro.readthedocs.io/en/stable/pages/tutorials/custom-actions-tutorial/#implicit-actions-chain
    page.get_by_role("gridcell", name="Europe").nth(0).click()
    check_http_requests_count(page, http_requests_paths, 4)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 4, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_drill_through_filter_graph(page, http_requests_paths):
    """Page with set_control action for filter graph on the different page."""
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.SET_CONTROL_DRILL_THROUGH_FILTER_GRAPH_SOURCE}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # filter drill_through between charts (3 http)
    # here we have 3 http requests because one is for set_control action
    # and two are for on page load that happens while opening a targeted page
    element = page.locator('path[class="point plotly-customdata"]').nth(20)
    box = element.bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    check_http_requests_count(page, http_requests_paths, 5)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 5, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_drill_through_parameter_graph(page, http_requests_paths):
    """Page with set_control action for parametrize graph on the different page."""
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.SET_CONTROL_DRILL_THROUGH_PARAMETER_GRAPH_SOURCE}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # parameter drill_through between charts (3 http)
    # here we have 3 http requests because one is for set_control action
    # and two are for on_page_load that happens while opening a targeted page
    element = page.locator('path[class="point plotly-customdata"]').nth(20)
    box = element.bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    check_http_requests_count(page, http_requests_paths, 5)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 5, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_drill_through_filter_ag_grid(page, http_requests_paths):
    """Page with set_control action for ag_grid filter graph on the different page."""
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.SET_CONTROL_DRILL_THROUGH_FILTER_AG_GRID_SOURCE}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # filter drill_through between charts (3 http)
    # here we have 3 http requests because one is for set_control action
    # and two are for on page load that happens while opening a targeted page
    page.get_by_role("gridcell", name="versicolor").nth(0).click()
    check_http_requests_count(page, http_requests_paths, 5)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 5, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_drill_down_graph(page, http_requests_paths):
    """Page with set_control action applied for the same graph as chain actions."""
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.SET_CONTROL_DRILL_DOWN_GRAPH_PAGE}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # filter drill_down for the same chart (4 http)
    # here we have 4 http requests because implicit actions chain triggered twice (two set_control actions in the chain)
    # https://vizro.readthedocs.io/en/stable/pages/tutorials/custom-actions-tutorial/#implicit-actions-chain
    element = page.locator('path[class="point plotly-customdata"]').nth(20)
    box = element.bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    check_http_requests_count(page, http_requests_paths, 6)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 6, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_reset_controls_header(page, http_requests_paths):
    # open the page (2 http)
    page.locator(f"a[href='/{cnst.TABLE_AG_GRID_INTERACTIONS_PAGE}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # click on the reset_controls button (1 http)
    page.locator("button[id$='reset_button']").click()
    check_http_requests_count(page, http_requests_paths, 3)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 3, sleep=cnst.HTTP_TIMEOUT_LONG)


@http_requests
def test_reset_controls_page(page, http_requests_paths):
    # open the page (2 http)
    page.locator(f"a[href='{cnst.FILTERS_INSIDE_CONTAINERS_PAGE_PATH}']").click()
    check_http_requests_count(page, http_requests_paths, 2)

    # click on the reset_controls button (1 http)
    page.locator("button[id$='reset_button']").click()
    check_http_requests_count(page, http_requests_paths, 3, sleep=3000)

    # checking that no additional http has occurred
    check_http_requests_count(page, http_requests_paths, 3, sleep=cnst.HTTP_TIMEOUT_LONG)
