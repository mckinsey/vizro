import os
import shutil
import subprocess
from pathlib import Path

import pandas as pd
import pytest
from e2e.vizro import constants as cnst
from hamcrest import assert_that, equal_to


def make_screenshot_and_paths(driver, request_node_name):
    """Creates image paths and makes screenshot during the test run."""
    result_image_path = f"{request_node_name}_branch.png"
    expected_image_path = (
        f"tests/e2e/screenshots/{os.getenv('BROWSER', 'chrome')}/{request_node_name.replace('test', 'main')}.png"
    )
    driver.save_screenshot(result_image_path)
    return result_image_path, expected_image_path


def assert_pixelmatch(result_image_path, expected_image_path):
    expected_image_name = Path(expected_image_path).name
    # pixelmatch docs: https://github.com/mapbox/pixelmatch
    subprocess.run(
        [
            "pixelmatch",
            expected_image_path,
            result_image_path,
            f"{expected_image_name.replace('.', '_difference_from_main.')}",
            cnst.PIXELMATCH_THRESHOLD,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    Path(f"{expected_image_name.replace('.', '_difference_from_main.')}").unlink()


def assert_image_equal(result_image_path, expected_image_path):
    """Comparison logic and diff files creation."""
    expected_image_name = Path(expected_image_path).name
    try:
        assert_pixelmatch(result_image_path, expected_image_path)
        Path(result_image_path).unlink()
    except subprocess.CalledProcessError as err:
        shutil.copy(result_image_path, expected_image_name)
        shutil.copy(expected_image_path, f"{expected_image_name.replace('.', '_old.')}")
        Path(result_image_path).unlink()
        raise Exception(err.stdout)


def assert_image_not_equal(image_one, image_two):
    try:
        assert_pixelmatch(image_one, image_two)
        pytest.fail("Images should be different")
    except subprocess.CalledProcessError:
        pass


def assert_files_equal(base_file, exported_file):
    df_first = pd.read_csv(base_file)
    df_second = pd.read_csv(exported_file)

    # Check rows in base_file that are missing in exported_file
    missing_in_exported = df_first[~df_first.apply(tuple, 1).isin(df_second.apply(tuple, 1))]

    # Check rows in exported_file that are missing in base_file
    missing_in_base = df_second[~df_second.apply(tuple, 1).isin(df_first.apply(tuple, 1))]

    differences = pd.concat([missing_in_exported, missing_in_base])

    assert_that(
        differences.empty,
        equal_to(True),
        reason=f"{exported_file} is not equal to {base_file}\nDifference is:\n{differences}",
    )
