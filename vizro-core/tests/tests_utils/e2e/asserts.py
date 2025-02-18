import os
import re
import shutil
import subprocess
from pathlib import Path

# import cv2
# import imutils
# from hamcrest import assert_that, equal_to
# def _compare_images(expected_image, result_image):
#     """Comparison process."""
#     # Subtract two images
#     difference = cv2.subtract(expected_image, result_image)
#     # Splitting image into separate channels
#     blue, green, red = cv2.split(difference)
#     # Counting non-zero pixels and comparing it to zero
#     assert_that(cv2.countNonZero(blue), equal_to(0), reason="Blue channel is different")
#     assert_that(cv2.countNonZero(green), equal_to(0), reason="Green channel is different")
#     assert_that(cv2.countNonZero(red), equal_to(0), reason="Red channel is different")
# def _create_image_difference(expected_image, result_image):
#     """Creates new image with diff of images comparison."""
#     # Calculate the difference between the two images
#     diff = cv2.absdiff(expected_image, result_image)
#     # Convert image to grayscale
#     gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
#     for i in range(0, 3):
#         # Dilation of the image
#         dilated = cv2.dilate(gray.copy(), None, iterations=i + 1)
#     # Apply threshold to the dilated image
#     (t_var, thresh) = cv2.threshold(dilated, 3, 255, cv2.THRESH_BINARY)
#     # Calculate difference contours for the image
#     cnts = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
#     cnts = imutils.grab_contours(cnts)
#     for contour in cnts:
#         # Calculate bounding rectangles around detected contour
#         (x, y, width, height) = cv2.boundingRect(contour)
#         # Draw red rectangle around difference area
#         cv2.rectangle(expected_image, (x, y), (x + width, y + height), (0, 0, 255), 2)
#     return expected_image
import pytest


def make_screenshot_and_paths(driver, request_node_name):
    """Creates image paths and makes screenshot during the test run."""
    result_image_path = f"{request_node_name}_branch.png"
    expected_image_path = (
        f"tests/e2e/screenshots/{os.getenv('BROWSER')}/{request_node_name.replace('test', 'main')}.png"
    )
    driver.save_screenshot(result_image_path)
    return result_image_path, expected_image_path


# def assert_image_equal(result_image_path, expected_image_path):
#     """Comparison logic and diff files creation."""
#     expected_image = Image.open(expected_image_path)
#     expected_image_name = Path(expected_image_path).name
#     result_image = Image.open(result_image_path)
#     diff_image = Image.new("RGBA", expected_image.size)
#     try:
#         pixelmatch(expected_image, result_image, diff_image, includeAA=True)
#         Path(result_image_path).unlink()
#     except AssertionError as exc:
#         # Copy created branch image to the one with the name from main for easier replacement in the repo
#         shutil.copy(result_image_path, expected_image_name)
#         # Writing image with differences to a new file
#         diff_image.save(f"{result_image_path}_difference_from_main.png")
#         raise AssertionError(exc)
#     except ValueError as exc:
#         shutil.copy(result_image_path, expected_image_name)
#         raise ValueError(exc)


def assert_image_equal(result_image_path, expected_image_path):
    """Comparison logic and diff files creation."""
    expected_image_name = Path(expected_image_path).name
    result = subprocess.run(
        [
            "pixelmatch",
            expected_image_path,
            result_image_path,
            f"{expected_image_name.replace('.', '_difference_from_main.')}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if "error: 0%" in result.stdout:
        Path(result_image_path).unlink()
        Path(f"{result_image_path}_difference_from_main.png").unlink()
        print(result.stdout)  # noqa: T201
    if "Image dimensions do not match:" in result.stdout or re.search(r"error:\s*([1-9]\d*|0*\.\d+)% ", result.stdout):
        shutil.copy(result_image_path, expected_image_name)
        shutil.copy(expected_image_path, f"{expected_image_name.replace('.', '_old.')}")
        Path(result_image_path).unlink()
        pytest.fail(result.stdout)
