import os
import sys
import requests

VERSION_MATCHSTR = r'\s*__version__\s*=\s*"(\d+\.\d+\.\d+)"'


# def get_package_version(base_path, package_path):
#     init_file_path = Path(base_path) / package_path / "__init__.py"
#     match_obj = re.search(VERSION_MATCHSTR, Path(init_file_path).read_text())
#     return match_obj.group(1)
### GET PACKAGE VERSION THROUGH HATCH (FOR FUTURE COMPATIBILITY)


def check_no_version_pypi(pypi_endpoint, package_name, package_version):
    print(f"Check if {package_name} {package_version} is on pypi")
    response = requests.get(pypi_endpoint, timeout=10)
    if response.status_code == 404:
        # Version doesn't exist on Pypi - do release
        print(f"Starting the release of {package_name} {package_version}")
        return True
    else:
        print(f"Skipped: {package_name} {package_version} already exists on PyPI")
        return False


if __name__ == "__main__":
    """Check if a package needs to be released"""
    new_release = "false"
    package_name = sys.argv[1]
    package_version = sys.argv[2]

    pypi_endpoint = f"https://pypi.org/pypi/{package_name}/{package_version}/json/"

    if check_no_version_pypi(pypi_endpoint, package_name, package_version):
        new_release = "true"

    env_file = os.getenv("GITHUB_ENV")
    with open(env_file, "a") as env_file:
        env_file.write(f"NEW_RELEASE={new_release}\n")
        if new_release == "true":
            env_file.write(f"PACKAGE_NAME={package_name}\nPACKAGE_VERSION={package_version}\n")
