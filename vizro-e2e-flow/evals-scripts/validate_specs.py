"""Validate that all 5 spec files exist with correct YAML structure and cross-spec consistency."""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml",
# ]
# ///

import json
import sys
from pathlib import Path

import yaml


def check_file_exists(spec_dir: Path, filename: str) -> dict:
    path = spec_dir / filename
    return {
        "check": f"{filename} exists",
        "status": "PASS" if path.exists() else "FAIL",
        "detail": str(path) if path.exists() else f"File not found: {path}",
    }


def load_yaml(spec_dir: Path, filename: str) -> tuple[dict | None, dict | None]:
    path = spec_dir / filename
    if not path.exists():
        return None, {"check": f"{filename} valid YAML", "status": "FAIL", "detail": "File does not exist"}
    try:
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict):
            return None, {"check": f"{filename} valid YAML", "status": "FAIL", "detail": "Root is not a mapping"}
        return data, {"check": f"{filename} valid YAML", "status": "PASS", "detail": ""}
    except yaml.YAMLError as e:
        return None, {"check": f"{filename} valid YAML", "status": "FAIL", "detail": str(e)}


def get_nested(data: dict, *keys):
    for k in keys:
        if not isinstance(data, dict) or k not in data:
            return None
        data = data[k]
    return data


def check_required_fields(data: dict | None, filename: str, field_paths: list[str]) -> list[dict]:
    results = []
    if data is None:
        for fp in field_paths:
            results.append({"check": f"{filename} has '{fp}'", "status": "FAIL", "detail": "Could not load file"})
        return results
    for fp in field_paths:
        keys = fp.split(".")
        val = get_nested(data, *keys)
        if val is not None:
            results.append({"check": f"{filename} has '{fp}'", "status": "PASS", "detail": ""})
        else:
            results.append({"check": f"{filename} has '{fp}'", "status": "FAIL", "detail": f"Missing key path: {fp}"})
    return results


def extract_page_names(data: dict | None) -> set[str]:
    if data is None:
        return set()
    pages = data.get("pages", [])
    if not isinstance(pages, list):
        return set()
    names = set()
    for p in pages:
        if isinstance(p, dict) and "name" in p:
            names.add(str(p["name"]).strip().lower())
    return names


def check_page_consistency(specs: dict[str, dict | None]) -> list[dict]:
    results = []
    names = {}
    for label, data in specs.items():
        names[label] = extract_page_names(data)

    all_labels = list(names.keys())
    for i, a in enumerate(all_labels):
        for b in all_labels[i + 1 :]:
            if not names[a] or not names[b]:
                results.append({
                    "check": f"Page names consistent: {a} vs {b}",
                    "status": "FAIL",
                    "detail": f"Could not extract page names from one or both specs ({a}: {names[a]}, {b}: {names[b]})",
                })
            elif names[a] == names[b]:
                results.append({
                    "check": f"Page names consistent: {a} vs {b}",
                    "status": "PASS",
                    "detail": f"Pages: {names[a]}",
                })
            else:
                only_a = names[a] - names[b]
                only_b = names[b] - names[a]
                results.append({
                    "check": f"Page names consistent: {a} vs {b}",
                    "status": "FAIL",
                    "detail": f"Only in {a}: {only_a}; Only in {b}: {only_b}",
                })
    return results


def validate(project_dir: str) -> dict:
    project = Path(project_dir)
    spec_dir = project / "spec"
    checks = []

    spec_files = {
        "1_information_architecture.yaml": {
            "fields": ["dashboard", "dashboard.name", "pages", "decisions"],
        },
        "2_interaction_ux.yaml": {
            "fields": ["pages", "decisions"],
        },
        "3_visual_design.yaml": {
            "fields": ["visualizations", "decisions"],
        },
        "4_implementation.yaml": {
            "fields": ["implementation", "implementation.app_file", "spec_compliance"],
        },
        "5_test_report.yaml": {
            "fields": ["testing", "testing.launch", "testing.navigation", "testing.console"],
        },
    }

    loaded = {}
    for filename, config in spec_files.items():
        checks.append(check_file_exists(spec_dir, filename))
        data, yaml_check = load_yaml(spec_dir, filename)
        if yaml_check:
            checks.append(yaml_check)
        loaded[filename] = data
        checks.extend(check_required_fields(data, filename, config["fields"]))

    # Cross-spec page name consistency for specs 1-3
    spec_page_data = {
        "spec/1": loaded.get("1_information_architecture.yaml"),
        "spec/2": loaded.get("2_interaction_ux.yaml"),
    }
    # spec/3 uses 'visualizations' not 'pages', so skip it for page name consistency
    checks.extend(check_page_consistency(spec_page_data))

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {"criterion": "spec_files_generated", "status": status, "checks": checks}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <project_dir>", file=sys.stderr)
        sys.exit(1)
    result = validate(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "PASS" else 1)
