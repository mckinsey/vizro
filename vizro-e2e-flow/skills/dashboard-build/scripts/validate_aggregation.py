"""Validate that bar/line charts use pre-aggregated data, not raw detail-level datasets."""

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

import ast
import json
import sys
from pathlib import Path

# Chart types that require pre-aggregated data (stacking raw rows produces broken visuals)
AGGREGATION_REQUIRED_CHARTS = {"bar", "line", "area", "funnel"}


class AggregationVisitor(ast.NodeVisitor):
    """Check that inline px.bar/px.line calls use pre-aggregated data."""

    def __init__(self, source_lines: list[str]):
        """Initialize with source lines for segment extraction."""
        self.source_lines = source_lines
        self.violations: list[dict] = []
        self.registered_datasets: dict[str, str] = {}  # name -> "raw" | "aggregated" | "unknown"
        self.capture_functions: set[str] = set()  # functions decorated with @capture

    def visit_Assign(self, node: ast.Assign):
        """Track data_manager registrations to identify raw vs aggregated datasets."""
        if not self._is_data_manager_subscript(node.targets):
            self.generic_visit(node)
            return
        key = self._get_subscript_key(node.targets[0])
        if not key:
            self.generic_visit(node)
            return
        # Get source text of the value expression to detect patterns
        value_src = ast.get_source_segment("\n".join(self.source_lines), node.value) or ""
        if "groupby" in value_src or "agg(" in value_src or ".sum()" in value_src or ".mean()" in value_src:
            self.registered_datasets[key] = "aggregated"
        elif "read_csv" in value_src or "read_excel" in value_src or "read_parquet" in value_src:
            self.registered_datasets[key] = "raw"
        else:
            self.registered_datasets[key] = "unknown"
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track @capture("graph") decorated functions — these handle their own aggregation."""
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                func_name = ""
                if isinstance(dec.func, ast.Name):
                    func_name = dec.func.id
                elif isinstance(dec.func, ast.Attribute):
                    func_name = dec.func.attr
                if func_name == "capture":
                    self.capture_functions.add(node.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Check inline px.bar/px.line calls for aggregation."""
        func_name = self._get_func_name(node)

        # Only check px.bar, px.line, etc. (not custom @capture functions)
        if "." in func_name:
            module, method = func_name.rsplit(".", 1)
            if module in ("px", "plotly.express", "vizro.plotly.express") and method in AGGREGATION_REQUIRED_CHARTS:
                # Check what data_frame is being passed
                data_ref = self._get_data_frame_arg(node)
                if data_ref:
                    dataset_type = self.registered_datasets.get(data_ref, "unknown")
                    if dataset_type == "raw":
                        self.violations.append(
                            {
                                "type": "raw_data_in_chart",
                                "chart_type": method,
                                "data_frame": data_ref,
                                "line": node.lineno,
                                "detail": f"px.{method}() uses raw dataset '{data_ref}' without aggregation. "
                                f"This will stack individual rows as separate rectangles.",
                            }
                        )
                    elif dataset_type == "unknown":
                        # Can't determine — flag as warning
                        self.violations.append(
                            {
                                "type": "possibly_raw_data",
                                "chart_type": method,
                                "data_frame": data_ref,
                                "line": node.lineno,
                                "detail": (
                                    f"px.{method}() uses dataset '{data_ref}' — cannot confirm if pre-aggregated. "
                                    f"Verify manually that data has one row per x-axis category."
                                ),
                            }
                        )

        self.generic_visit(node)

    def _get_func_name(self, node: ast.Call) -> str:
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
            elif isinstance(node.func.value, ast.Attribute) and isinstance(node.func.value.value, ast.Name):
                return f"{node.func.value.value.id}.{node.func.value.attr}.{node.func.attr}"
            return node.func.attr
        elif isinstance(node.func, ast.Name):
            return node.func.id
        return ""

    def _get_data_frame_arg(self, node: ast.Call) -> str | None:
        """Extract the data_frame argument (first positional or keyword)."""
        # Check first positional arg
        if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            return node.args[0].value
        # Check keyword
        for kw in node.keywords:
            if kw.arg == "data_frame" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                return kw.value.value
        return None

    def _is_data_manager_subscript(self, targets) -> bool:
        if not targets:
            return False
        t = targets[0]
        return isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and t.value.id == "data_manager"

    def _get_subscript_key(self, node) -> str | None:
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            return str(node.slice.value)
        return None


def validate(project_dir: str) -> dict:
    """Validate that bar/line/area/funnel charts use pre-aggregated data."""
    project = Path(project_dir)
    app_path = project / "app.py"
    checks = []

    if not app_path.exists():
        return {
            "criterion": "charts_use_preaggregated_data",
            "status": "FAIL",
            "checks": [{"check": "app.py exists", "status": "FAIL", "detail": "File not found"}],
        }

    source = app_path.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {
            "criterion": "charts_use_preaggregated_data",
            "status": "FAIL",
            "checks": [{"check": "app.py parses", "status": "FAIL", "detail": str(e)}],
        }

    visitor = AggregationVisitor(source.splitlines())
    visitor.visit(tree)

    if not visitor.violations:
        checks.append({"check": "All charts use pre-aggregated data", "status": "PASS", "detail": ""})
    else:
        for v in visitor.violations:
            status = "FAIL" if v["type"] == "raw_data_in_chart" else "WARN"
            checks.append(
                {
                    "check": f'Line {v["line"]}: px.{v["chart_type"]}(data_frame="{v["data_frame"]}")',
                    "status": status,
                    "detail": v["detail"],
                }
            )

    hard_checks = [c for c in checks if c["status"] != "WARN"]
    status = "PASS" if all(c["status"] == "PASS" for c in hard_checks) else "FAIL"
    return {"criterion": "charts_use_preaggregated_data", "status": status, "checks": checks}


if __name__ == "__main__":
    if len(sys.argv) != 2:  # noqa: PLR2004
        print(f"Usage: {sys.argv[0]} <project_dir>", file=sys.stderr)  # noqa: T201
        sys.exit(1)
    result = validate(sys.argv[1])
    print(json.dumps(result, indent=2))  # noqa: T201
    sys.exit(0 if result["status"] == "PASS" else 1)
