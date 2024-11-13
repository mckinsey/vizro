import subprocess

import cv2
import imutils
from hamcrest import assert_that, equal_to


def comparison_logic(original_image, new_image):
    """Comparison process."""
    difference = cv2.subtract(original_image, new_image)
    blue, green, red = cv2.split(difference)
    assert_that(cv2.countNonZero(blue), equal_to(0), reason="Blue channel is different")
    assert_that(
        cv2.countNonZero(green), equal_to(0), reason="Green channel is different"
    )
    assert_that(cv2.countNonZero(red), equal_to(0), reason="Red channel is different")


def create_image_difference(original, new):
    """Creates new image with diff of images comparison."""
    diff = original.copy()
    cv2.absdiff(original, new, diff)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    for i in range(0, 3):
        dilated = cv2.dilate(gray.copy(), None, iterations=i + 1)
    (t_var, thresh) = cv2.threshold(dilated, 3, 255, cv2.THRESH_BINARY)
    cnts = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    for contour in cnts:
        (x, y, width, height) = cv2.boundingRect(contour)
        cv2.rectangle(new, (x, y), (x + width, y + height), (0, 255, 0), 2)
    return new


def compare_images(browserdriver, base_image, test_image_name):
    """Comparison logic and diff files creation."""
    browserdriver.save_screenshot(f"{test_image_name}_branch.png")
    original = cv2.imread(f"screenshots/{base_image}")
    new = cv2.imread(f"{test_image_name}_branch.png")
    try:
        comparison_logic(original, new)
        subprocess.call(f"rm -rf {test_image_name}_branch.png", shell=True)
    except (AssertionError, AttributeError) as exp:
        subprocess.call(f"cp {test_image_name}_branch.png {base_image}", shell=True)
        diff = create_image_difference(original=new, new=original)
        cv2.imwrite(f"{test_image_name}_diff_main.png", diff)
        raise Exception("pictures are not the same") from exp
    except cv2.error as exp:
        subprocess.call(f"cp {test_image_name}_branch.png {base_image}", shell=True)
        raise Exception("pictures has different sizes") from exp