import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_http_requests_count
from playwright.sync_api import sync_playwright


def http_requests(func):
    """Decorator for setting up playwright logic and clear http requests paths list before main test."""

    def wrapper(request):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            http_requests_paths = []

            def on_request(request):
                if any(r in request.url for r in ["_dash-update-component"]):
                    http_requests_paths.append(request.url.split("/")[3])

            page.on("request", on_request)

            try:
                page.goto("http://127.0.0.1:5002/")
                page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
                check_http_requests_count(http_requests_paths, "_dash-update-component", 1)
                http_requests_paths.clear()

                func(page, http_requests_paths)

            except Exception:
                page.screenshot(path=f"{request.node.name}.png", full_page=True)
                raise

            finally:
                browser.close()

    return wrapper


@http_requests
def test_page_without_chart(page, http_requests_paths):
    # click on the button that creates only 1 request
    page.get_by_role("button").nth(1).click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    # check that only 1 request was created
    check_http_requests_count(http_requests_paths, "_dash-update-component", 1)
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_LONG)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 1)


@http_requests
def test_page_with_one_chart(page, http_requests_paths):
    # open the page with one chart
    page.locator(f"a[href='/{cnst.PAGE_WITH_ONE_CHART}']").click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    # check that only 2 requests were created
    check_http_requests_count(http_requests_paths, "_dash-update-component", 2)
    # delete one value from filter
    page.get_by_text("×").nth(0).click()  # noqa RUF001
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    # check that only 1 request was created
    check_http_requests_count(http_requests_paths, "_dash-update-component", 3)
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_LONG)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 3)


@http_requests
def test_button_with_three_actions(page, http_requests_paths):
    page.locator(f"a[href='/{cnst.PAGE_BUTTON_WITH_THREE_ACTIONS}']").click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 2)
    # click on the button that creates 3 requests
    page.get_by_role("button").nth(1).click()
    page.wait_for_timeout(3000)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 5)
    # choose value "Americas" in radio items filter
    page.get_by_text("Americas").nth(0).click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 6)
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_LONG)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 6)


@http_requests
def test_chart_with_filter_interaction(page, http_requests_paths):
    page.locator(f"a[href='/{cnst.PAGE_CHART_WITH_FILTER_INTERACTION}']").click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 2)
    # interact with the box chart
    element = page.locator(".box").nth(1)
    box = element.bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 3)
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_LONG)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 3)


@http_requests
def test_ag_grid_with_filter_interaction(page, http_requests_paths):
    page.locator(f"a[href='/{cnst.PAGE_AG_GRID_WITH_FILTER_INTERACTION}']").click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 2)
    # click on the cell in ag_grid
    page.get_by_role("gridcell", name="Europe").nth(0).click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 3)
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_LONG)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 3)


@http_requests
def test_dynamic_parametrisation(page, http_requests_paths):
    page.locator(f"a[href='/{cnst.PAGE_DYNAMIC_PARAMETRISATION}']").click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 2)
    # reload the page and wait till all network processes would be finished
    page.reload(wait_until="networkidle")
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 4)
    # choose value "Americas" in radio items filter
    page.get_by_text("Oceania").nth(0).click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 5)
    # check that "Oceania" present in dropdown filter and click it
    page.locator(".Select-arrow").click()
    page.locator('div[class="VirtualizedSelectOption"]').get_by_text("Oceania").click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 6)
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_LONG)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 6)


@http_requests
def test_all_selectors(page, http_requests_paths):
    """Page with all selector present."""
    page.locator(f"a[href='/{cnst.PAGE_ALL_SELECTORS}']").click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 2)
    # reload the page and wait till all network processes would be finished
    page.reload(wait_until="networkidle")
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 4)
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_LONG)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 4)


@http_requests
def test_actions_chain(page, http_requests_paths):
    page.locator(f"a[href='/{cnst.PAGE_ACTIONS_CHAIN}']").click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 1)
    # click on the button that creates action chain with 2 requests
    page.get_by_role("button").nth(1).click()
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_SHORT)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 3)
    page.wait_for_timeout(cnst.HTTP_TIMEOUT_LONG)
    check_http_requests_count(http_requests_paths, "_dash-update-component", 3)
