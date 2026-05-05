"""Generate the components compendium HTML from YAML data and a Jinja2 template.

Usage:
    hatch run compendium          Regenerate docs/pages/components_compendium/index.html
    hatch run compendium-check    Verify index.html is in sync with compendium_data.yaml (used in CI)

The workflow for adding a new component:
    1. Add an entry to docs/pages/components_compendium/compendium_data.yaml.
    2. Add a screenshot to docs/pages/components_compendium/assets/images/.
    3. Run `hatch run compendium` to regenerate index.html.
    4. Commit both compendium_data.yaml and index.html.
"""

import argparse
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

import vizro.actions as va
import vizro.models as vm

TOOLS_DIR = Path(__file__).parent
COMPENDIUM_DIR = TOOLS_DIR.parent / "docs" / "pages" / "components_compendium"
DATA_FILE = COMPENDIUM_DIR / "compendium_data.yaml"
TEMPLATE_FILE = TOOLS_DIR / "compendium_template.html"
OUTPUT_FILE = COMPENDIUM_DIR / "index.html"

# Models in vm.__all__ that are intentionally not visual components and don't need a
# compendium entry. When adding a new model, either add it to compendium_data.yaml or
# justify its exclusion here.
EXCLUDED_MODELS = {
    "VizroBaseModel",  # internal base class
    "Accordion",
    "NavBar",
    "NavLink",
    "Navigation",  # navigation config models
    "Action",  # action config wrapper, not a standalone visual component
    "Dashboard",
    "Page",  # top-level structural config
    "Layout",  # legacy alias for Grid (Grid is already covered)
    "Tooltip",  # utility attached to other components
    "ControlGroup",  # grouping utility, not a standalone visual component
    "Table",  # covered by AgGrid; vm.Table wraps Dash DataTable, less commonly used
}

# Actions in va.__all__ that are intentionally excluded from the compendium.
EXCLUDED_ACTIONS = {
    "filter_interaction",  # implicit framework action, not directly user-invoked
    "update_notification",  # paired with show_notification, covered in the same entry
}

# Maps public API name → expected HTML id, for items whose id doesn't follow simple lowercasing.
ID_OVERRIDES = {
    "export_data": "export-data",
    "set_control": "set-control",
    "show_notification": "notifications",
}


def get_yaml_ids(data: dict) -> set[str]:
    """Collect all component ids defined in the YAML data."""
    ids: set[str] = set()
    for category in data.get("categories", []):
        for item in category.get("items", []):
            ids.add(item["id"])
            for selector in item.get("selectors", []):
                ids.add(selector["id"])
    return ids


def check_coverage(data: dict) -> list[str]:
    """Return a list of error messages for public API items missing from the YAML."""
    yaml_ids = get_yaml_ids(data)
    errors = []

    required_models = set(vm.__all__) - EXCLUDED_MODELS
    for name in sorted(required_models):
        expected_id = ID_OVERRIDES.get(name, name.lower().replace("_", ""))
        if expected_id not in yaml_ids:
            errors.append(f"  vm.{name} (expected id '{expected_id}') is missing from compendium_data.yaml")

    required_actions = set(va.__all__) - EXCLUDED_ACTIONS
    for name in sorted(required_actions):
        expected_id = ID_OVERRIDES.get(name, name.lower().replace("_", ""))
        if expected_id not in yaml_ids:
            errors.append(f"  va.{name} (expected id '{expected_id}') is missing from compendium_data.yaml")

    return errors


def render() -> str:
    """Render index.html from compendium_data.yaml and compendium_template.html."""
    from vizro import __version__

    data = yaml.safe_load(DATA_FILE.read_text())
    env = Environment(
        loader=FileSystemLoader(str(TOOLS_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(TEMPLATE_FILE.name)
    return template.render(vizro_version=__version__, **data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="Check if index.html is up to date")
    args = parser.parse_args()

    data = yaml.safe_load(DATA_FILE.read_text())

    if args.check:
        coverage_errors = check_coverage(data)
        if coverage_errors:
            sys.exit(
                "Components compendium is missing entries for public API members.\n"
                "Add them to compendium_data.yaml or justify their exclusion in "
                "EXCLUDED_MODELS / EXCLUDED_ACTIONS in tools/generate_compendium.py:\n" + "\n".join(coverage_errors)
            )

        rendered = render()
        existing = OUTPUT_FILE.read_text()
        if existing != rendered:
            sys.exit(
                "docs/pages/components_compendium/index.html is out of date. "
                "Run `hatch run compendium` to regenerate it, then commit both "
                "index.html and compendium_data.yaml."
            )
        print("Components compendium is up to date.")
    else:
        rendered = render()
        OUTPUT_FILE.write_text(rendered)
        print(f"Generated {OUTPUT_FILE.relative_to(TOOLS_DIR.parent)}")


if __name__ == "__main__":
    main()
