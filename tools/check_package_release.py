"""Determine if new package should be release (based on version) and consequently write information to env."""
import os
import subprocess
import sys

import requests

AVAILABLE_PACKAGES = ["vizro-core", "vizro-ai"]
VERSION_MATCHSTR = r'\s*__version__\s*=\s*"(\d+\.\d+\.\d+)"'
RESPONSE_ERROR = 404


def _check_no_version_pypi(package_name, package_version):
    if package_name == "vizro-core":
        pypi_endpoint = f"https://pypi.org/pypi/vizro/{package_version}/json/"
    else:
        pypi_endpoint = f"https://pypi.org/pypi/{package_name}/{package_version}/json/"
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
    new_release = False
    number_of_releases = False
    env_file = str(os.getenv("GITHUB_ENV"))

    for package_name in AVAILABLE_PACKAGES:
        package_version = subprocess.check_output(["hatch", "version"], cwd=f"{package_name}").decode("utf-8").strip()

        if _check_no_dev_version(package_name, package_version) and _check_no_version_pypi(
            package_name, package_version
        ):
            if new_release:
                sys.exit("Cannot release two packages at the same time. Please modify your PR.")
            new_release = True

        with open(env_file, "a") as f:
            f.write(f"NEW_RELEASE={str(new_release)}\n")
            if new_release:
                f.write(f"PACKAGE_NAME={package_name}\nPACKAGE_VERSION={package_version}\n")
