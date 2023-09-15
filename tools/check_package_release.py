"""Determine if new package should be release (based on version) and consequently write information to env."""
import os
import sys

import requests

VERSION_MATCHSTR = r'\s*__version__\s*=\s*"(\d+\.\d+\.\d+)"'
RESPONSE_ERROR = 404


def _check_no_version_pypi(pypi_endpoint, package_name, package_version):
    response = requests.get(pypi_endpoint, timeout=10)
    if response.status_code == RESPONSE_ERROR:
        # Version doesn't exist on Pypi - do release
        print(f"Potential release of {package_name} {package_version}")  # noqa: T201
        return True
    else:
        print(f"Skipped: {package_name} {package_version} already exists on PyPI")  # noqa: T201
        return False


def _check_no_dev_version(package_name, package_version):
    if "dev" not in package_version:
        return True
    else:
        print(f"Skipped: {package_name} {package_version} is still under development")  # noqa: T201
        return False


if __name__ == "__main__":
    """Check if a package needs to be released"""
    new_release = False
    double_release = False
    package_name = sys.argv[1]
    package_version = sys.argv[2]

    pypi_endpoint = f"https://pypi.org/pypi/{package_name}/{package_version}/json/"

    if _check_no_dev_version(package_name, package_version) and _check_no_version_pypi(
        pypi_endpoint, package_name, package_version
    ):
        new_release = True

    env_file = os.getenv("GITHUB_ENV")

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
            f.write(f"PACKAGE_NAME={package_name}\nPACKAGE_VERSION={package_version}\n")
