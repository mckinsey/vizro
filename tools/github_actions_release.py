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
        print(f"Potential release of {package_name} {package_version}")
        return True
    else:
        print(f"Skipped: {package_name} {package_version} already exists on PyPI")
        return False

def check_dev_version(package_name, package_version):
    if "dev" in package_version:
        print(f"Skipped: {package_name} {package_version} is still under development")
        return True
    else:
        return False

if __name__ == "__main__":
    """Check if a package needs to be released"""
    new_release = "false"
    package_name = sys.argv[1]
    package_version = "0.1.1"#sys.argv[2]

    pypi_endpoint = f"https://pypi.org/pypi/{package_name}/{package_version}/json/"
    

    if not check_dev_version(package_name,package_version) and check_no_version_pypi(pypi_endpoint, package_name, package_version):
        new_release = "true"

    env_file = os.getenv("GITHUB_ENV")
    
    if os.path.exists(env_file) and new_release == "true":
        with open(env_file, "r") as f:
            for line in f:
                print(line)
                if line.strip() == "NEW_RELEASE=true":
                    sys.exit("Cannot release two packages at the same time. Please modify your PR.")

    with open(env_file, "a") as f:
        f.write(f"NEW_RELEASE={new_release}\n")
        if new_release == "true":
            f.write(f"PACKAGE_NAME={package_name}\nPACKAGE_VERSION={package_version}\n")
