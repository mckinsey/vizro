"""Determine if new package should be release (based on version) and consequently write information to env."""
import os
import re
import sys

import requests
from werkzeug.utils import secure_filename

VERSION_MATCHSTR = r'\s*__version__\s*=\s*"(\d+\.\d+\.\d+)"'
RESPONSE_ERROR = 404
ARG_NUM = 3


def _check_no_version_pypi(pypi_endpoint, package_name, package_version):
    response = requests.get(pypi_endpoint, timeout=10)
    if response.status_code == RESPONSE_ERROR:
        # Version doesn't exist on Pypi - do release
        print(f"Potential release of {package_name} {package_version}")  # noqa: T201
        return True
    else:
        print(f"Skipped: {package_name} {package_version} already exists on PyPI")  # noqa: T201
        return False


def _check_valid_version(package_version):
    pattern = re.compile("^(?P<major>0|[1-9]\\d*)\\.(?P<minor>0|[1-9]\\d*)\\.(?P<patch>0|[1-9]\\d*)$")
    if not pattern.match(str(package_version)):
        raise ValueError(f"Release version {package_version} not compatible with a semantic versioning release.")


def _check_valid_package_name(package_name):
    available_packages = ["vizro-core"]
    if package_name not in available_packages:
        raise ValueError(f"Package name {package_name} not in known list of packages.")


def _check_no_dev_version(package_name, package_version):
    if "dev" not in package_version:
        return True
    else:
        print(f"Skipped: {package_name} {package_version} is still under development")  # noqa: T201
        return False


if __name__ == "__main__":
    if len(sys.argv) != ARG_NUM:
        raise TypeError("Usage: python check_package_release.py <package_name> <package_version>")

    PACKAGE_NAME = sys.argv[1]
    PACKAGE_VERSION = sys.argv[2]

    _check_valid_package_name(PACKAGE_NAME)
    _check_valid_version(PACKAGE_VERSION)

    PYPI_ENDPOINT = f"https://pypi.org/pypi/{PACKAGE_NAME}/{PACKAGE_VERSION}/json/"

    new_release = False
    double_release = False

    if _check_no_dev_version(PACKAGE_NAME, PACKAGE_VERSION) and _check_no_version_pypi(
        PYPI_ENDPOINT, PACKAGE_NAME, PACKAGE_VERSION
    ):
        new_release = True

    env_file = secure_filename(os.getenv("GITHUB_ENV"))

    if os.path.exists(env_file) and new_release:
        with open(env_file, "r") as f:
            for line in f:
                if line.strip() == "NEW_RELEASE=True":
                    double_release = True

    if double_release:
        sys.exit("Cannot release two packages at the same time. Please modify your PR.")

    with open(env_file, "a") as f:
        f.write(f"NEW_RELEASE={str(new_release)}\n")
        if new_release:
            f.write(f"PACKAGE_NAME={PACKAGE_NAME}\nPACKAGE_VERSION={PACKAGE_VERSION}\n")
