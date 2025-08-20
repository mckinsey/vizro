import pytest
from playwright.async_api import async_playwright
import asyncio
from playwright.sync_api import sync_playwright
import json
from hamcrest import assert_that, equal_to
from collections import Counter


def check_requests_count(urls_list, url_path, requests_number):
    counts = Counter(urls_list)
    assert_that(counts[url_path], equal_to(requests_number),
                reason=f"'{url_path}' should be equal to {requests_number}")


urls = []


def http_requests(func):

    def wrapper(request):
        global urls
        urls = []

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()

            def on_request(request):
                if any(p in request.url for p in ["_dash-update-component", "_dash-dependencies", "_dash-layout"]):
                    urls.append(request.url.split('/')[3])

            page.on("request", on_request)
            try:
                page.goto("http://127.0.0.1:5002/")

                func(page)

                # Keep the browser open for observation
                page.wait_for_timeout(5000)  # 5 seconds

            except Exception as e:
                page.screenshot(path=f"{request.node.name}.png", full_page=True)
                print(f"Test failed, screenshot saved: {e}")
                raise

            finally:
                context.close()
                browser.close()

    return wrapper


@http_requests
def test_1(page):
    page.get_by_text("×").nth(0).click()

    check_requests_count(urls, "_dash-update-component", 3)
    check_requests_count(urls, "_dash-dependencies", 1)
    check_requests_count(urls, "_dash-layout", 1)


@http_requests
def test_2(page):
    page.locator("a[href='/export-data---custom-sleep-action---export-data---1-guard']").click()
    page.get_by_text("Export data").nth(0).click()
    page.get_by_text("Americas").nth(0).click()

    check_requests_count(urls, "_dash-update-component",4)
    check_requests_count(urls, "_dash-dependencies", 1)
    check_requests_count(urls, "_dash-layout", 1)


@http_requests
def test_3(page):
    page.locator("a[href='/filter-interaction-graph---1-guard']").click()
    element = page.locator(".box").nth(1)
    box = element.bounding_box()
    page.mouse.click(
        box["x"] + box["width"] / 2,
        box["y"] + box["height"] / 2
    )

    check_requests_count(urls, "_dash-update-component", 4)
    check_requests_count(urls, "_dash-dependencies", 1)
    check_requests_count(urls, "_dash-layout", 1)


@http_requests
def test_4(page):
    page.locator("a[href='/filter-interaction-grid---2-guards']").click()
    page.get_by_role("gridcell", name="Europe").nth(0).click()

    check_requests_count(urls, "_dash-update-component", 4)
    check_requests_count(urls, "_dash-dependencies", 1)
    check_requests_count(urls, "_dash-layout", 1)


@http_requests
def test_5(page):
    page.locator("a[href='/dynamic-filter---2-guards']").click()
    page.get_by_text("Asia").nth(0).click()

    check_requests_count(urls, "_dash-update-component", 4)
    check_requests_count(urls, "_dash-dependencies", 1)
    check_requests_count(urls, "_dash-layout", 1)


@http_requests
def test_6(page):
    page.locator("a[href='/dataframe-parameter---2-guards']").click()
    page.get_by_text("Oceania").nth(0).click()
    page.locator(".Select-arrow").click()
    page.locator(".form-check-input").nth(0).click()

    check_requests_count(urls, "_dash-update-component", 5)
    check_requests_count(urls, "_dash-dependencies", 1)
    check_requests_count(urls, "_dash-layout", 1)


@http_requests
def test_7(page):
    page.locator("a[href='/url-parameter-filters---2-guards-on-refresh']").click()
    page.reload(wait_until="networkidle")

    check_requests_count(urls, "_dash-update-component", 5)
    check_requests_count(urls, "_dash-dependencies", 2)
    check_requests_count(urls, "_dash-layout", 2)


@http_requests
def test_8(page):
    page.locator("a[href='/multi-url-parameter-filters---3-guards-or-refresh']").click()
    page.get_by_text("Asia").nth(0).click()
    page.get_by_text("Asia").nth(1).click()
    page.reload(wait_until="networkidle")

    check_requests_count(urls, "_dash-update-component", 7)
    check_requests_count(urls, "_dash-dependencies", 2)
    check_requests_count(urls, "_dash-layout", 2)


@http_requests
def test_9(page):
    page.locator("a[href='/dataframe-parameter-and-url-filter--2-guards']").click()
    page.get_by_text("Africa").nth(0).click()
    page.locator(".Select-arrow").click()
    page.locator(".form-check-input").nth(0).click()

    check_requests_count(urls, "_dash-update-component", 5)
    check_requests_count(urls, "_dash-dependencies", 1)
    check_requests_count(urls, "_dash-layout", 1)


@http_requests
def test_10(page):
    page.locator("a[href='/dfp--dynamic-filter--url--filter-interaction---5-guards-on-refresh']").click()
    page.get_by_text("Africa").nth(0).click()
    page.locator(".Select-arrow").click()
    page.locator(".form-check-input").nth(0).click()
    page.reload(wait_until="networkidle")

    check_requests_count(urls, "_dash-update-component", 7)
    check_requests_count(urls, "_dash-dependencies", 2)
    check_requests_count(urls, "_dash-layout", 2)


# @pytest.mark.asyncio
# async def http_requests_async():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch()
#         context = await browser.new_context()
#         page = await context.new_page()
#
#         async def on_request(request):
#             # sizes() only works after request finishes → get from the response
#             response = await request.response()
#             if response:
#                 sizes = await request.sizes()
#                 print(f"URL: {request.url}")
#                 print(sizes)
#
#         page.on("requestfinished", on_request)
#
#         await page.goto("http://127.0.0.1:5002/")
#         await asyncio.sleep(5)
#         await browser.close()
#
#
# def log_request(request):
#     if request.method == "POST":
#         print(f"\n➡️ {request.method} {request.url}")
#         print("Headers:")
#         for key, value in request.headers.items():
#             print(f"  {key}: {value}")
#         try:
#             post_data = request.post_data
#             print(f"Body:\n{post_data}")
#         except Exception as e:
#             print("Could not get post data:", e)
#
#
# def log_response(response):
#     print(f"\n⬅️ {response.status} {response.url}")
#     try:
#         body = response.text()
#         print("Response Body (truncated to 500 chars):")
#         print(body[:500])
#     except Exception as e:
#         print("Could not read response body:", e)

# def make_on_request(urls):
#     def on_request(request):
#         if any(p in request.url for p in ["_dash-update-component", "_dash-dependencies", "_dash-layout"]):
#             # print(f"REQUEST: {request.method} {request.url}")
#             urls.append(request.url.split('/')[3])
#             # try:
#             #     print("Body:", request.post_data)
#             #     # If JSON, pretty print
#             #     print("Body JSON:", json.dumps(json.loads(request.post_data), indent=2))
#             # except Exception:
#             #     pass
#     return on_request


# # Listen for their responses
# def on_response(response):
#     if any(p in response.url for p in ["_dash-update-component", "_dash-dependencies", "_dash-layout"]):
#         print(f"RESPONSE: {response.url}")
#         # try:
#         #     body = response.body()
#         #     print("Response JSON:", json.dumps(json.loads(body), indent=2))
#         # except Exception:
#         #     pass
