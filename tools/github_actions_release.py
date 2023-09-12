"""Determine if new package should be release (based on version) and consequently write information to env."""
import os
import sys

import requests

VERSION_MATCHSTR = r'\s*__version__\s*=\s*"(\d+\.\d+\.\d+)"'
RESPONSE_ERROR = 404


# def get_package_version(base_path, package_path):
#     init_file_path = Path(base_path) / package_path / "__init__.py"
#     match_obj = re.search(VERSION_MATCHSTR, Path(init_file_path).read_text())
#     return match_obj.group(1)
### GET PACKAGE VERSION THROUGH HATCH (FOR FUTURE COMPATIBILITY)


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
        return True  # TODO: CHANGE TO FALSE AFTER TESTING
    else:
        print(f"Skipped: {package_name} {package_version} is still under development")  # noqa: T201
        return True


if __name__ == "__main__":
    """Check if a package needs to be released"""
    new_release = "false"
    double_release = False
    package_name = sys.argv[1]
    package_version = sys.argv[2]  # "0.1.1" if package_name=="vizro" else "0.1.0.dev0"#

    pypi_endpoint = f"https://pypi.org/pypi/{package_name}/{package_version}/json/"

    if _check_no_dev_version(package_name, package_version) and _check_no_version_pypi(
        pypi_endpoint, package_name, package_version
    ):
        new_release = "true"

    env_file = os.getenv("GITHUB_ENV")

    if os.path.exists(env_file) and new_release == "true":
        with open(env_file, "r") as f:
            for line in f:
                if line.strip() == "NEW_RELEASE=true":
                    double_release = True

    with open(env_file, "a") as f:
        f.write(f"NEW_RELEASE={new_release}\n")
        if new_release == "true":
            f.write(f"PACKAGE_NAME={package_name}\nPACKAGE_VERSION={package_version}\n")

    if double_release:
        sys.exit("Cannot release two packages at the same time. Please modify your PR.")
