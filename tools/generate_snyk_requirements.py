"""FUNCTION TO GENERATE REQUIREMENTS.TXT AND OPTIONAL_REQUIREMENTS.TXT FILES."""

import argparse
import sys
from pathlib import Path

import toml

requirements_file = Path("snyk/requirements.txt")


def __parse_pyproject_toml():
    """Parse pyproject.toml to get project dependencies and optional dependencies."""
    pyproject = toml.loads(Path("pyproject.toml").read_text())

    dependencies = pyproject.get("project", {}).get("dependencies", {})
    optional_dependencies = pyproject.get("project", {}).get("optional-dependencies", {})
    requirements = dependencies + [item for sublist in optional_dependencies.values() for item in sublist]

    return requirements


requirements_toml = __parse_pyproject_toml()
parser = argparse.ArgumentParser(description="Generate requirements.txt from pyproject.toml")
parser.add_argument("--check", help="check requirements.txt is up to date", action="store_true")
args = parser.parse_args()

if args.check:
    requirements_txt = requirements_file.read_text().splitlines()

    if requirements_txt != requirements_toml:
        sys.exit(
            "`requirements.txt` is out of sync with the `pyproject.toml`. Please run `hatch run "
            "update-snyk-requirements` to update your requirements.txt file before merging."
        )
    print("`requirements.txt` is up to date.")  # noqa: T201
else:
    requirements_file.write_text("\n".join(requirements_toml) + "\n")
