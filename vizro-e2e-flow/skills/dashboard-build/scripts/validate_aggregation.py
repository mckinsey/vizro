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

    def __init__(self, source: str):
        """Initialize with the full source string for AST segment extraction."""
        self.source = source
        self.violations: list[dict] = []
        self.registered_datasets: dict[str, str] = {}  # name -> "raw" | "aggregated" | "unknown"
        # local_name -> original method name (e.g. {"my_bar": "bar"}) for
        # `from (vizro.)plotly.express import bar [as my_bar]` style imports.
        # Without this, a bare ``bar(...)`` call slips past the aggregation check.
        self.imported_chart_funcs: dict[str, str] = {}

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track aggregation-required chart names imported from (vizro.)plotly.express."""
        if node.module in ("plotly.express", "vizro.plotly.express"):
            for alias in node.names:
                if alias.name in AGGREGATION_REQUIRED_CHARTS:
                    local = alias.asname or alias.name
                    self.imported_chart_funcs[local] = alias.name
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        """Track data_manager registrations to identify raw vs aggregated datasets."""
        if not self._is_data_manager_subscript(node.targets):
            self.generic_visit(node)
            return
        key = self._get_subscript_key(node.targets[0])
        if not key:
            self.generic_visit(node)
            return
        value_src = ast.get_source_segment(self.source, node.value) or ""
        if "groupby" in value_src or "agg(" in value_src or ".sum()" in value_src or ".mean()" in value_src:
            self.registered_datasets[key] = "aggregated"
        elif "read_csv" in value_src or "read_excel" in value_src or "read_parquet" in value_src:
            self.registered_datasets[key] = "raw"
        else:
            self.registered_datasets[key] = "unknown"
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Check inline px.bar/px.line (and equivalent bare-name) calls for aggregation."""
        func_name = self._get_func_name(node)
        method: str | None = None

        if "." in func_name:
            module, last = func_name.rsplit(".", 1)
            if module in ("px", "plotly.express", "vizro.plotly.express") and last in AGGREGATION_REQUIRED_CHARTS:
                method = last
        elif func_name in self.imported_chart_funcs:
            # Bare ``bar(...)`` from ``from (vizro.)plotly.express import bar [as ...]``.
            method = self.imported_chart_funcs[func_name]

        if method is not None:
            self._check_aggregation(node, method)

        self.generic_visit(node)

    def _check_aggregation(self, node: ast.Call, method: str) -> None:
        """Record a violation if the chart call uses raw or unknown data."""
        data_ref = self._get_data_frame_arg(node)
        if not data_ref:
            return
        dataset_type = self.registered_datasets.get(data_ref, "unknown")
        if dataset_type == "raw":
            self._record(
                "raw_data_in_chart",
                node,
                method,
                data_ref,
                (
                    f"Line {node.lineno}: px.{method}(data_frame='{data_ref}') uses raw "
                    f"detail-level data without aggregation. This will stack individual rows "
                    f"as separate rectangles instead of summing them. "
                    f"FIX: Move this chart into a @capture('graph') custom function that "
                    f"aggregates with .groupby().sum()/.mean() before calling px.{method}(). "
                    f"Example: agg = data_frame.groupby('x_col', as_index=False)['y_col'].sum(); "
                    f"fig = px.{method}(agg, x='x_col', y='y_col')"
                ),
            )
        elif dataset_type == "unknown":
            self._record(
                "possibly_raw_data",
                node,
                method,
                data_ref,
                (
                    f"Line {node.lineno}: px.{method}(data_frame='{data_ref}') — cannot confirm "
                    f"if data is pre-aggregated. If '{data_ref}' has multiple rows per x-axis "
                    f"category, bars/lines will stack instead of summing. FIX: Move "
                    f"this chart into a @capture('graph') function that aggregates inside."
                ),
            )

    def _record(self, vtype: str, node: ast.Call, method: str, data_ref: str, detail: str) -> None:
        self.violations.append(
            {
                "type": vtype,
                "chart_type": method,
                "data_frame": data_ref,
                "line": node.lineno,
                "detail": detail,
            }
        )

    def _get_func_name(self, node: ast.Call) -> str:
        """Return the dotted call name, walking arbitrary-depth attribute chains."""
        func = node.func
        if isinstance(func, ast.Name):
            return func.id
        if not isinstance(func, ast.Attribute):
            return ""
        parts: list[str] = []
        cur: ast.AST = func
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
            return ".".join(reversed(parts))
        return func.attr

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

    visitor = AggregationVisitor(source)
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
