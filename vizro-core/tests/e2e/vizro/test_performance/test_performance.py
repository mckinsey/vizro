import re

from hamcrest import assert_that
from playwright.sync_api import sync_playwright
from werkzeug.http import parse_options_header


def performance(func):
    """Decorator for setting up playwright logic."""

    def wrapper(request):
        """Simple test to measure request timings."""
        with sync_playwright() as p:
            # selecting the Chromium browser engine which starts a new browser instance
            browser = p.chromium.launch()
            # creating browser context - clean, isolated browser profile
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            # creating a new page inside the context
            page = context.new_page()
            response_times = []

            def on_request(request):
                if any(r in request.url for r in ["_dash-update-component"]):
                    timing = request.timing
                    request_type = re.findall(r"__(.*?)_[0-9a-f-]{8,}", request.post_data_json["output"])
                    request_time = timing["responseEnd"] - timing["requestStart"]
                    server_timing = parse_options_header(request.response().all_headers().get("server-timing", ""))[
                        1
                    ].get("dur", 0)
                    if request_type:
                        response_times.append(
                            {
                                "request_type": request_type[0],
                                "request_time": request_time,
                                "server_timing": int(server_timing),
                            }
                        )

            page.on("requestfinished", on_request)

            page.goto("http://127.0.0.1:5002/")

            func(page, response_times)

            browser.close()

    return wrapper


@performance
def test_time(page, response_times):
    """Simple test to measure request timings."""
    page.locator(".dash-dropdown .Select-value-icon:nth-of-type(1)").nth(0).click()
    page.get_by_text("petal_length").click()
    page.wait_for_load_state("networkidle")
    print(response_times)  # noqa
    assert_that(
        response_times[0]["request_time"] < 1500,
        reason=f"request time for {response_times[0]['request_type']} is higher than 1500ms",
    )
    assert_that(
        response_times[1]["request_time"] < 5000,
        reason=f"request time for {response_times[1]['request_type']} is higher than 5000ms",
    )
    assert_that(
        response_times[2]["request_time"] < 5000,
        reason=f"request time for {response_times[2]['request_type']} is higher than 5000ms",
    )
    assert_that(
        response_times[0]["server_timing"] < 1300,
        reason=f"server timing for {response_times[0]['request_type']} is higher than 1300ms",
    )
    assert_that(
        response_times[1]["server_timing"] < 1300,
        reason=f"server timing for {response_times[1]['request_type']} is higher than 1300ms",
    )
    assert_that(
        response_times[2]["server_timing"] < 1300,
        reason=f"request time for {response_times[2]['request_type']} is higher than 13000ms",
    )
