"""
Specification Loader for Vizro Dashboard Development

This script loads and validates all specification files from previous development stages.
It MUST be run before any implementation to ensure designs are followed correctly.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_specifications(spec_dir: Path = None) -> Dict[str, Any]:
    """
    Load ALL specs from previous stages - THIS IS MANDATORY

    Args:
        spec_dir: Path to the spec directory. Defaults to 'spec' in current directory.

    Returns:
        Dictionary containing all loaded specifications
    """
    if spec_dir is None:
        spec_dir = Path("spec")

    spec_dir.mkdir(exist_ok=True)

    specs = {}
    spec_files = [
        "1_information_architecture.yaml",
        "2_interaction_ux.yaml",
        "3_visual_design.yaml"
    ]

    for spec_file in spec_files:
        file_path = spec_dir / spec_file
        if file_path.exists():
            with open(file_path, 'r') as f:
                specs[spec_file] = yaml.safe_load(f)
            print(f"✓ Loaded {spec_file}")
        else:
            print(f"⚠ Warning: {spec_file} not found")

    return specs


def main():
    """Main function to load specs and generate implementation checklist"""

    print("Loading specifications from previous stages...")
    specs = load_specifications()

    if not specs:
        print("❌ No specifications found! Please complete previous stages first.")
        return

    return specs


if __name__ == "__main__":
    specs = main()