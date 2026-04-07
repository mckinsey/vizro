"""Validate grid layout rules: 12-column, rectangularity, and sizing constraints."""

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


def check_twelve_columns(grid_pattern: list[list[int]], page_name: str) -> list[dict]:
    checks = []
    all_twelve = True
    for i, row in enumerate(grid_pattern):
        if len(row) != 12:
            all_twelve = False
            checks.append({
                "check": f"{page_name}: row {i} has 12 columns",
                "status": "FAIL",
                "detail": f"Row {i} has {len(row)} columns: {row}",
            })
    if all_twelve:
        checks.append({
            "check": f"{page_name}: all rows have 12 columns",
            "status": "PASS",
            "detail": f"{len(grid_pattern)} rows checked",
        })
    return checks


def check_rectangularity(grid_pattern: list[list[int]], page_name: str) -> list[dict]:
    checks = []
    # Collect column positions for each component index
    component_cols: dict[int, dict[int, set[int]]] = {}
    for row_idx, row in enumerate(grid_pattern):
        for col_idx, comp_id in enumerate(row):
            if comp_id < 0:  # -1 = empty cell
                continue
            if comp_id not in component_cols:
                component_cols[comp_id] = {}
            if row_idx not in component_cols[comp_id]:
                component_cols[comp_id][row_idx] = set()
            component_cols[comp_id][row_idx].add(col_idx)

    all_rectangular = True
    for comp_id, rows_dict in sorted(component_cols.items()):
        col_sets = list(rows_dict.values())
        if len(set(frozenset(s) for s in col_sets)) > 1:
            all_rectangular = False
            checks.append({
                "check": f"{page_name}: component {comp_id} is rectangular",
                "status": "FAIL",
                "detail": f"Component {comp_id} spans different columns in different rows: {dict(rows_dict)}",
            })

    if all_rectangular:
        checks.append({
            "check": f"{page_name}: all components form rectangles",
            "status": "PASS",
            "detail": f"{len(component_cols)} components checked",
        })
    return checks


def check_row_min_height(page_data: dict, page_name: str) -> list[dict]:
    rmh = page_data.get("row_min_height")
    if rmh is None:
        return [{"check": f"{page_name}: row_min_height", "status": "PASS", "detail": "Not specified (ok)"}]
    if str(rmh).strip('"').strip("'") == "140px":
        return [{"check": f"{page_name}: row_min_height is 140px", "status": "PASS", "detail": ""}]
    return [{
        "check": f"{page_name}: row_min_height is 140px",
        "status": "FAIL",
        "detail": f"Found: {rmh}",
    }]


def check_component_sizing(grid_pattern: list[list[int]], page_name: str) -> list[dict]:
    """Advisory checks for component sizing (warnings, not hard fails)."""
    advisories = []
    component_spans: dict[int, dict] = {}

    for row_idx, row in enumerate(grid_pattern):
        for col_idx, comp_id in enumerate(row):
            if comp_id < 0:
                continue
            if comp_id not in component_spans:
                component_spans[comp_id] = {"rows": set(), "cols": set()}
            component_spans[comp_id]["rows"].add(row_idx)
            component_spans[comp_id]["cols"].add(col_idx)

    for comp_id, spans in sorted(component_spans.items()):
        n_rows = len(spans["rows"])
        n_cols = len(spans["cols"])
        # Charts should be at least 3 rows tall (except KPI cards which are 1 row)
        if n_rows == 2:
            advisories.append({
                "check": f"{page_name}: component {comp_id} sizing advisory",
                "status": "WARN",
                "detail": f"Component {comp_id} spans {n_cols} cols x {n_rows} rows. "
                f"2 rows is unusual — KPIs should be 1 row, charts should be 3+.",
            })

    return advisories


def validate(project_dir: str) -> dict:
    project = Path(project_dir)
    spec2_path = project / "spec" / "2_interaction_ux.yaml"
    checks = []

    if not spec2_path.exists():
        return {
            "criterion": "grid_layout_enforced",
            "status": "FAIL",
            "checks": [{"check": "spec/2_interaction_ux.yaml exists", "status": "FAIL", "detail": "File not found"}],
        }

    try:
        data = yaml.safe_load(spec2_path.read_text())
    except yaml.YAMLError as e:
        return {
            "criterion": "grid_layout_enforced",
            "status": "FAIL",
            "checks": [{"check": "spec/2 valid YAML", "status": "FAIL", "detail": str(e)}],
        }

    pages = data.get("pages", [])
    if not isinstance(pages, list) or not pages:
        return {
            "criterion": "grid_layout_enforced",
            "status": "FAIL",
            "checks": [{"check": "spec/2 has pages", "status": "FAIL", "detail": "No pages found"}],
        }

    for page in pages:
        page_name = page.get("name", "unnamed")
        grid_pattern = page.get("grid_pattern")
        if not grid_pattern or not isinstance(grid_pattern, list):
            checks.append({
                "check": f"{page_name}: grid_pattern exists",
                "status": "FAIL",
                "detail": "Missing or invalid grid_pattern",
            })
            continue

        checks.append({"check": f"{page_name}: grid_pattern exists", "status": "PASS", "detail": ""})
        checks.extend(check_twelve_columns(grid_pattern, page_name))
        checks.extend(check_rectangularity(grid_pattern, page_name))
        checks.extend(check_row_min_height(page, page_name))
        checks.extend(check_component_sizing(grid_pattern, page_name))

    # Only count PASS/FAIL for status (WARN doesn't cause failure)
    hard_checks = [c for c in checks if c["status"] != "WARN"]
    status = "PASS" if all(c["status"] == "PASS" for c in hard_checks) else "FAIL"
    return {"criterion": "grid_layout_enforced", "status": status, "checks": checks}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <project_dir>", file=sys.stderr)
        sys.exit(1)
    result = validate(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "PASS" else 1)
