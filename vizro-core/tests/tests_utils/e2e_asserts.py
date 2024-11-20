import shutil
from pathlib import Path

import cv2
import imutils
from hamcrest import assert_that, equal_to


def _compare_images(expected_image, result_image):
    """Comparison process."""
    difference = cv2.subtract(expected_image, result_image)
    blue, green, red = cv2.split(difference)
    assert_that(cv2.countNonZero(blue), equal_to(0), reason="Blue channel is different")
    assert_that(cv2.countNonZero(green), equal_to(0), reason="Green channel is different")
    assert_that(cv2.countNonZero(red), equal_to(0), reason="Red channel is different")


def _create_image_difference(expected_image, result_image):
    """Creates new image with diff of images comparison."""
    diff = expected_image.copy()
    cv2.absdiff(expected_image, result_image, diff)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    for i in range(0, 3):
        dilated = cv2.dilate(gray.copy(), None, iterations=i + 1)
    (t_var, thresh) = cv2.threshold(dilated, 3, 255, cv2.THRESH_BINARY)
    cnts = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    for contour in cnts:
        (x, y, width, height) = cv2.boundingRect(contour)
        cv2.rectangle(result_image, (x, y), (x + width, y + height), (0, 255, 0), 2)
    return result_image


def make_screenshot_and_paths(browserdriver, request):
    result_image_path = f"{request.node.name}_branch.png"
    expected_image_name = f"{request.node.name.replace('test', 'main')}.png"
    expected_image_path = f"tests/e2e/screenshots/{expected_image_name}"
    browserdriver.save_screenshot(result_image_path)
    return result_image_path, expected_image_path, expected_image_name


def assert_image_equal(result_image_path, expected_image_path, expected_image_name):
    """Comparison logic and diff files creation."""
    expected_image = cv2.imread(expected_image_path)
    result_image = cv2.imread(result_image_path)
    try:
        _compare_images(expected_image, result_image)
        Path(result_image_path).unlink()
    except AssertionError as exc:
        shutil.copy(result_image_path,  expected_image_name)
        diff = _create_image_difference(expected_image=expected_image, result_image=result_image)
        cv2.imwrite(f"{result_image_path}_difference_from_main.png", diff)
        raise AssertionError("pictures are not the same") from exc
    except cv2.error as exc:
        shutil.copy(result_image_path, expected_image_name)
        raise cv2.error("pictures has different sizes") from exc
