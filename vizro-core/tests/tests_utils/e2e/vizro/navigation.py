import time
from datetime import datetime

from e2e.vizro import constants as cnst
from e2e.vizro.checkers import check_accordion_active
from e2e.vizro.paths import (
    dropdown_deselect_all_path,
    dropdown_id_path,
    dropdown_select_all_path,
    page_title_path,
)
from e2e.vizro.waiters import callbacks_finish_waiter, graph_load_waiter
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def click_element_by_xpath_selenium(driver, xpath):
    WebDriverWait(driver, timeout=cnst.SELENIUM_WAITERS_TIMEOUT).until(
        expected_conditions.element_to_be_clickable((By.XPATH, xpath))
    ).click()


def hover_over_element_by_xpath_selenium(driver, xpath):
    element = driver.find_element(By.XPATH, xpath)
    ActionChains(driver).move_to_element(element).perform()


def hover_over_element_by_css_selector_selenium(driver, css_selector):
    element = driver.find_element(By.CSS_SELECTOR, css_selector)
    ActionChains(driver).move_to_element(element).perform()


def hover_over_and_click_by_css_selector_selenium(driver, css_selector):
    element = driver.find_element(By.CSS_SELECTOR, css_selector)
    ActionChains(driver).move_to_element(element).click().perform()


def modifier_click(dash_br, selector, key):
    """Clicking an element while holding a modifier key (like Shift or Ctrl)."""
    element = dash_br.find_element(selector)
    ActionChains(dash_br.driver).key_down(key).click(element).key_up(key).perform()


def accordion_select(driver, accordion_name):
    """Selecting accordion and checking if it is active."""
    click_element_by_xpath_selenium(driver.driver, f"//button[text()='{accordion_name}']")
    check_accordion_active(driver, accordion_name)
    # to let accordion open
    time.sleep(1)


def page_select(driver, page_name, graph_check=True, page_path=None):
    """Selecting page and checking if it has proper title."""
    page_path = page_path or f"/{page_name}"
    driver.multiple_click(f"a[href='{page_path}']", 1)

    driver.wait_for_contains_text(page_title_path(), page_name)
    if graph_check:
        graph_load_waiter(driver)


def page_select_selenium(driver, page_path, page_name, timeout=cnst.SELENIUM_WAITERS_TIMEOUT, graph_check=True):
    """Selecting page and checking if it has proper title for pure selenium."""
    WebDriverWait(driver, timeout).until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, f"a[href='{page_path}']"))
    ).click()
    WebDriverWait(driver, timeout).until(
        expected_conditions.text_to_be_present_in_element((By.CSS_SELECTOR, page_title_path()), page_name)
    )
    if graph_check:
        WebDriverWait(driver, timeout).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class='dash-graph'] path[class='xtick ticks crisp']")
            )
        )


def select_single_time_picker_value(driver, elem_id, hour, minute):
    """Set a single TimePicker value (HH:MM).

    Clicks outside the control after entry to trigger debounce and waits for Dash callbacks to finish.

    Args:
        driver: dash_br fixture.
        elem_id: id of the TimePicker wrapper (without -start/-end suffix).
        hour: two-digit hour string.
        minute: two-digit minute string.
    """
    _set_time_picker_fields(driver, elem_id, hour, minute)
    driver.find_element("body").click()
    callbacks_finish_waiter(driver)


def select_range_time_picker_value(driver, elem_id, start_hour, start_minute, end_hour, end_minute):
    """Set a range TimePicker value (HH:MM).

    Fills both "From" and "To" inputs before blurring once so the dcc.Store receives a complete [start, end] tuple.

    Args:
        driver: dash_br fixture.
        elem_id: id of the range TimePicker (dcc.Store id, without -start/-end suffix).
        start_hour: two-digit hour string for the "From" input.
        start_minute: two-digit minute string for the "From" input.
        end_hour: two-digit hour string for the "To" input.
        end_minute: two-digit minute string for the "To" input.
    """
    _set_time_picker_fields(driver, f"{elem_id}-start", start_hour, start_minute)
    _set_time_picker_fields(driver, f"{elem_id}-end", end_hour, end_minute)
    driver.find_element("body").click()
    callbacks_finish_waiter(driver)


def _set_time_picker_fields(driver, elem_id, hour, minute):
    """Fill hour and minute fields of one dmc.TimePicker input (used by single and range selectors)."""
    fields = driver.find_elements(f"div[id='{elem_id}'] input.mantine-TimePicker-field")
    for field, part in zip(fields, [hour, minute]):
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(part)
        field.send_keys(Keys.TAB)
        time.sleep(0.3)


def _iso_date_to_aria_label(iso_date):
    """Convert an ISO date string to the dmc calendar day button aria-label."""
    dt = datetime.strptime(iso_date, "%Y-%m-%d")
    return f"{dt.day} {dt.strftime('%B')} {dt.year}"


def _click_displayed_calendar_control(driver, css_selector_within_calendar):
    """Click a control inside the topmost visible calendar popover."""
    timeout = cnst.SELENIUM_WAITERS_TIMEOUT
    poll_interval = 0.2
    elapsed = 0
    while elapsed < timeout:
        for calendar in reversed(driver.driver.find_elements(By.CSS_SELECTOR, 'div[data-calendar="true"]')):
            if not calendar.is_displayed():
                continue
            controls = calendar.find_elements(By.CSS_SELECTOR, css_selector_within_calendar)
            if controls:
                driver.driver.execute_script("arguments[0].click();", controls[0])
                return
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError(f"Displayed calendar control not found: {css_selector_within_calendar}")


def _parse_calendar_month_year(driver):
    """Read the month currently shown in an open dmc.DatePickerInput calendar."""
    timeout = cnst.SELENIUM_WAITERS_TIMEOUT
    poll_interval = 0.2
    elapsed = 0
    while elapsed < timeout:
        for calendar in reversed(driver.driver.find_elements(By.CSS_SELECTOR, 'div[data-calendar="true"]')):
            if not calendar.is_displayed():
                continue
            for level in calendar.find_elements(By.CSS_SELECTOR, ".mantine-DatePickerInput-calendarHeaderLevel"):
                level_text = level.text.strip()
                if level_text:
                    return datetime.strptime(level_text, "%B %Y")
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError("Calendar header did not populate")


def _navigate_calendar_to_month(driver, year, month):
    """Navigate an open calendar to the requested month."""
    for _ in range(24):
        displayed = _parse_calendar_month_year(driver)
        if displayed.year == year and displayed.month == month:
            return
        diff = (year - displayed.year) * 12 + (month - displayed.month)
        direction = "next" if diff > 0 else "previous"
        _click_displayed_calendar_control(
            driver,
            f'button.mantine-DatePickerInput-calendarHeaderControl[data-direction="{direction}"]',
        )
        time.sleep(0.2)
    raise TimeoutError(f"Could not navigate calendar to {year}-{month:02d}")


def _select_date_picker_input_date(driver, date_elem_id, iso_date):
    """Open a dmc.DatePickerInput calendar, navigate to the target month, and select the date."""
    target = datetime.strptime(iso_date, "%Y-%m-%d")
    driver.multiple_click(f'button[id="{date_elem_id}"]', 1)
    driver.wait_for_element('div[data-calendar="true"]')
    time.sleep(0.3)
    _navigate_calendar_to_month(driver, target.year, target.month)
    _click_displayed_calendar_control(driver, f'button[aria-label="{_iso_date_to_aria_label(iso_date)}"]')
    time.sleep(0.2)


def select_single_datetime_picker_value(driver, elem_id, iso_date, hour, minute):
    """Set a single DateTimePicker value (date + HH:MM).

    Clicks outside the control after entry to trigger debounce and waits for Dash callbacks to finish.

    Args:
        driver: dash_br fixture.
        elem_id: id of the DateTimePicker proxy dcc.Store (without -date/-time suffix).
        iso_date: target date as "YYYY-MM-DD".
        hour: two-digit hour string.
        minute: two-digit minute string.
    """
    _select_date_picker_input_date(driver, f"{elem_id}-date", iso_date)
    _set_time_picker_fields(driver, f"{elem_id}-time", hour, minute)
    driver.find_element("body").click()
    callbacks_finish_waiter(driver)


def select_range_datetime_picker_value(driver, elem_id, start, end):
    """Set a range DateTimePicker value (date + optional HH:MM for both ends).

    Dates are always required. Pass ``None`` for hour/minute on either side to leave that time cleared;
    the filter then treats the date-only value as start-of-day (From) or end-of-day (To).

    Args:
        driver: dash_br fixture.
        elem_id: id of the range DateTimePicker proxy dcc.Store.
        start: tuple of (ISO date "YYYY-MM-DD", hour, minute) for the "From" inputs.
        end: tuple of (ISO date "YYYY-MM-DD", hour, minute) for the "To" inputs.
    """
    start_iso_date, start_hour, start_minute = start
    end_iso_date, end_hour, end_minute = end
    _select_date_picker_input_date(driver, f"{elem_id}-date-start", start_iso_date)
    _select_date_picker_input_date(driver, f"{elem_id}-date-end", end_iso_date)
    if start_hour is not None and start_minute is not None:
        _set_time_picker_fields(driver, f"{elem_id}-time-start", start_hour, start_minute)
    if end_hour is not None and end_minute is not None:
        _set_time_picker_fields(driver, f"{elem_id}-time-end", end_hour, end_minute)
    time.sleep(0.5)  # allow debounced TimePicker values to flush into the proxy dcc.Store
    driver.find_element("body").click()
    callbacks_finish_waiter(driver)


def select_range_time_picker_value_playwright(page, elem_id, start_hour, start_minute, end_hour, end_minute):
    """Set a range TimePicker value (HH:MM) using Playwright."""
    _set_time_picker_fields_playwright(page, f"{elem_id}-start", start_hour, start_minute)
    _set_time_picker_fields_playwright(page, f"{elem_id}-end", end_hour, end_minute)
    page.locator("body").click()


def _click_displayed_calendar_control_playwright(page, css_selector_within_calendar):
    """Click a control inside the topmost visible calendar popover using Playwright."""
    deadline = time.time() + cnst.SELENIUM_WAITERS_TIMEOUT
    while time.time() < deadline:
        for calendar in reversed(page.locator('div[data-calendar="true"]').all()):
            if not calendar.is_visible():
                continue
            control = calendar.locator(css_selector_within_calendar).first
            if control.count():
                control.click(force=True)
                return
        page.wait_for_timeout(200)
    raise TimeoutError(f"Displayed calendar control not found: {css_selector_within_calendar}")


def _parse_calendar_month_year_playwright(page):
    """Read the month currently shown in an open dmc.DatePickerInput calendar using Playwright."""
    deadline = time.time() + cnst.SELENIUM_WAITERS_TIMEOUT
    while time.time() < deadline:
        for calendar in reversed(page.locator('div[data-calendar="true"]').all()):
            if not calendar.is_visible():
                continue
            level_text = calendar.locator(".mantine-DatePickerInput-calendarHeaderLevel").first.inner_text().strip()
            if level_text:
                return datetime.strptime(level_text, "%B %Y")
        page.wait_for_timeout(200)
    raise TimeoutError("Calendar header did not populate")


def _navigate_calendar_to_month_playwright(page, year, month):
    """Navigate an open calendar to the requested month using Playwright."""
    for _ in range(24):
        displayed = _parse_calendar_month_year_playwright(page)
        if displayed.year == year and displayed.month == month:
            return
        diff = (year - displayed.year) * 12 + (month - displayed.month)
        direction = "next" if diff > 0 else "previous"
        _click_displayed_calendar_control_playwright(
            page,
            f'button.mantine-DatePickerInput-calendarHeaderControl[data-direction="{direction}"]',
        )
        page.wait_for_timeout(200)
    raise TimeoutError(f"Could not navigate calendar to {year}-{month:02d}")


def _select_date_picker_input_date_playwright(page, date_elem_id, iso_date):
    """Open a dmc.DatePickerInput calendar, navigate to the target month, and select the date."""
    target = datetime.strptime(iso_date, "%Y-%m-%d")
    page.locator(f'button[id="{date_elem_id}"]').click()
    page.wait_for_selector('div[data-calendar="true"]')
    page.wait_for_timeout(300)
    _navigate_calendar_to_month_playwright(page, target.year, target.month)
    _click_displayed_calendar_control_playwright(page, f'button[aria-label="{_iso_date_to_aria_label(iso_date)}"]')
    page.wait_for_timeout(200)


def select_range_datetime_picker_value_playwright(page, elem_id, start, end):
    """Set a range DateTimePicker value (date + optional HH:MM for both ends) using Playwright."""
    start_iso_date, start_hour, start_minute = start
    end_iso_date, end_hour, end_minute = end
    _select_date_picker_input_date_playwright(page, f"{elem_id}-date-start", start_iso_date)
    _select_date_picker_input_date_playwright(page, f"{elem_id}-date-end", end_iso_date)
    if start_hour is not None and start_minute is not None:
        _set_time_picker_fields_playwright(page, f"{elem_id}-time-start", start_hour, start_minute)
    if end_hour is not None and end_minute is not None:
        _set_time_picker_fields_playwright(page, f"{elem_id}-time-end", end_hour, end_minute)
    page.wait_for_timeout(500)
    page.locator("body").click()


def _set_time_picker_fields_playwright(page, elem_id, hour, minute):
    """Fill hour and minute fields of one dmc.TimePicker input via Playwright."""
    fields = page.locator(f"div[id='{elem_id}'] input.mantine-TimePicker-field").all()
    for field, part in zip(fields, [hour, minute]):
        field.click()
        field.press("Control+a")
        field.fill(part)
        page.wait_for_timeout(300)


def select_slider_value(driver, elem_id, min_value=None, max_value=None):
    if min_value:
        min_value_elem = driver.find_element(f"div[id='{elem_id}'] input[class$='dash-range-slider-min-input']")
        driver.clear_input(min_value_elem)
        min_value_elem.send_keys(str(min_value))
        min_value_elem.send_keys(Keys.TAB)
    # set `max_value` for setting single vm.Slider value
    else:
        max_value_elem = driver.find_element(f"div[id='{elem_id}'] input[class$='dash-range-slider-max-input']")
        driver.clear_input(max_value_elem)
        max_value_elem.send_keys(str(max_value))
        max_value_elem.send_keys(Keys.TAB)


def clear_dropdown(driver, dropdown_id):
    driver.multiple_click(f"{dropdown_id_path(dropdown_id)} .dash-dropdown-clear", 1)


def select_dropdown_value(driver, dropdown_id, value):
    """Steps to select value in dropdown."""
    # if dropdown is open, close it to avoid errors with selecting value
    if driver.find_elements(f"{dropdown_id_path(dropdown_id)}[aria-expanded='true']"):
        driver.multiple_click(dropdown_id_path(dropdown_id), 1)
    driver.select_dcc_dropdown(dropdown_id_path(dropdown_id), value)
    # if dropdown is open, close it to avoid errors with selecting other controls
    if driver.find_elements(f"{dropdown_id_path(dropdown_id)}[aria-expanded='true']"):
        driver.multiple_click(dropdown_id_path(dropdown_id), 1)


def select_dropdown_select_all(driver, dropdown_id):
    """Steps to select Select All value in dropdown."""
    # if dropdown is closed, open it to avoid errors with selecting value
    if driver.find_elements(f"{dropdown_id_path(dropdown_id)}[aria-expanded='false']"):
        driver.multiple_click(dropdown_id_path(dropdown_id), 1)
    driver.multiple_click(dropdown_select_all_path(dropdown_id), 1)


def select_dropdown_deselect_all(driver, dropdown_id):
    """Steps to select Deselect All value in dropdown."""
    # if dropdown is open, close it to avoid errors with selecting value
    if driver.find_elements(f"{dropdown_id_path(dropdown_id)}[aria-expanded='false']"):
        driver.multiple_click(dropdown_id_path(dropdown_id), 1)
    driver.multiple_click(dropdown_deselect_all_path(dropdown_id), 1)
