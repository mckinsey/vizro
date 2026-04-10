"""Validate Vizro color consistency: no hardcoded colors in app.py, no color_decisions in spec/3."""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml",
# ]
# ///

import ast
import json
import re
import sys
from pathlib import Path

import yaml

# All valid Vizro hex colors — keep in sync with vizro-core/src/vizro/themes/_colors.py
# These are whitelisted — using them explicitly (e.g. for AG Grid styling) is acceptable.
VIZRO_HEX_COLORS = frozenset(
    {
        "#097DFE",
        "#6F39E3",
        "#05D0F0",
        "#0F766E",
        "#8C8DE9",
        "#11B883",
        "#E77EC2",
        "#C84189",
        "#C0CA33",
        "#3E495B",
        "#DBEBFE",
        "#BDDCFE",
        "#8CC6FF",
        "#4BA5FF",
        "#0063F6",
        "#004DE0",
        "#0B40B4",
        "#163B8B",
        "#EBE9FC",
        "#DAD6FB",
        "#C0B6FB",
        "#A08AF8",
        "#855FF6",
        "#6630D5",
        "#5529B1",
        "#47268E",
        "#D2F9FC",
        "#AAF2FA",
        "#68E8F7",
        "#00B7D4",
        "#0092B2",
        "#087490",
        "#155E74",
        "#1A4E61",
        "#D4F9E7",
        "#ADF1D3",
        "#73E6BA",
        "#2CD099",
        "#07966B",
        "#0B7859",
        "#0F5E48",
        "#114D3C",
        "#F8E9F5",
        "#F3D3EB",
        "#EDAFDD",
        "#DB5AB1",
        "#C84194",
        "#AB3478",
        "#8D2D63",
        "#742A53",
        "#F4F9D2",
        "#EAF3A9",
        "#DBE973",
        "#CBD740",
        "#979912",
        "#76720C",
        "#605B11",
        "#514C15",
        "#EFF1F4",
        "#E0E4E9",
        "#C9D0D9",
        "#97A1B0",
        "#6D788A",
        "#505C6F",
        "#2A3241",
        "#1D222E",
        "#D0FAF3",
        "#A1F4E8",
        "#64E9D9",
        "#1BD0C1",
        "#00B5A9",
        "#00918A",
        "#0F5B59",
        "#144B49",
        "#FBE4E2",
        "#FACDC9",
        "#F7AAA3",
        "#F1766C",
        "#EA5748",
        "#D63A28",
        "#B22F20",
        "#922A20",
        "#782921",
        "#FFF7CD",
        "#FFED9B",
        "#FFE16A",
        "#FFD545",
        "#FFC107",
        "#DBA005",
        "#B78103",
        "#936402",
        "#7A4F01",
        "#FFFFFF",
        "#000000",
    }
)
VIZRO_HEX_LOWER = frozenset(c.lower() for c in VIZRO_HEX_COLORS)

# Keyword arguments that indicate hardcoded color usage in px.* calls
FORBIDDEN_COLOR_KWARGS = {
    "color_discrete_map",
    "color_discrete_sequence",
    "color_continuous_scale",
    "marker_color",
}

# Layout overrides that violate "let Vizro handle colors"
FORBIDDEN_LAYOUT_KWARGS = {
    "plot_bgcolor",
    "paper_bgcolor",
    "colorway",
}

HEX_PATTERN = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")


class ColorVisitor(ast.NodeVisitor):
    """AST visitor to detect color violations in Python source."""

    def __init__(self):
        """Initialize violation tracking state."""
        self.violations: list[dict] = []
        self.imports_vizro_themes = False

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track imports from vizro.themes."""
        if node.module and "vizro.themes" in node.module:
            self.imports_vizro_themes = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Check function calls for forbidden color and layout kwargs."""
        func_name = self._get_func_name(node)

        # Check for forbidden keyword arguments in any function call
        for kw in node.keywords:
            if kw.arg in FORBIDDEN_COLOR_KWARGS:
                self.violations.append(
                    {
                        "type": "forbidden_color_kwarg",
                        "kwarg": kw.arg,
                        "function": func_name,
                        "line": node.lineno,
                    }
                )
            if kw.arg in FORBIDDEN_LAYOUT_KWARGS:
                self.violations.append(
                    {
                        "type": "forbidden_layout_kwarg",
                        "kwarg": kw.arg,
                        "function": func_name,
                        "line": node.lineno,
                    }
                )

        # Check string literal arguments for hex colors
        for kw in node.keywords:
            self._check_hex_in_node(kw.value, func_name, kw.arg, node.lineno)

        self.generic_visit(node)

    def _check_hex_in_node(self, node: ast.AST, func_name: str, kwarg: str | None, line: int):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            matches = HEX_PATTERN.findall(node.value)
            for m in matches:
                if m.lower() not in VIZRO_HEX_LOWER:
                    self.violations.append(
                        {
                            "type": "non_vizro_hex_color",
                            "color": m,
                            "function": func_name,
                            "kwarg": kwarg,
                            "line": line,
                        }
                    )
        elif isinstance(node, (ast.List, ast.Tuple)):
            for elt in node.elts:
                self._check_hex_in_node(elt, func_name, kwarg, line)
        elif isinstance(node, ast.Dict):
            for v in node.values:
                if v is not None:
                    self._check_hex_in_node(v, func_name, kwarg, line)

    def _get_func_name(self, node: ast.Call) -> str:
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
            return node.func.attr
        elif isinstance(node.func, ast.Name):
            return node.func.id
        return "<unknown>"


def check_app_py(project_dir: Path) -> list[dict]:
    """Check app.py for hardcoded color violations."""
    checks = []
    app_path = project_dir / "app.py"
    if not app_path.exists():
        checks.append({"check": "app.py exists", "status": "FAIL", "detail": "File not found"})
        return checks

    checks.append({"check": "app.py exists", "status": "PASS", "detail": ""})

    source = app_path.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        checks.append({"check": "app.py parses", "status": "FAIL", "detail": str(e)})
        return checks

    visitor = ColorVisitor()
    visitor.visit(tree)

    if not visitor.violations:
        checks.append({"check": "app.py has no color violations", "status": "PASS", "detail": ""})
    else:
        for v in visitor.violations:
            if v["type"] == "forbidden_color_kwarg":
                checks.append(
                    {
                        "check": f"app.py: no '{v['kwarg']}' in {v['function']}",
                        "status": "FAIL",
                        "detail": f"Line {v['line']}: {v['function']}({v['kwarg']}=...)",
                    }
                )
            elif v["type"] == "forbidden_layout_kwarg":
                checks.append(
                    {
                        "check": f"app.py: no '{v['kwarg']}' override",
                        "status": "FAIL",
                        "detail": f"Line {v['line']}: {v['function']}({v['kwarg']}=...)",
                    }
                )
            elif v["type"] == "non_vizro_hex_color":
                checks.append(
                    {
                        "check": "app.py: no non-Vizro hex color",
                        "status": "FAIL",
                        "detail": f"Line {v['line']}: {v['color']} in {v['function']}({v.get('kwarg', '?')}=...)",
                    }
                )

    if visitor.imports_vizro_themes:
        checks.append(
            {
                "check": "app.py imports vizro.themes (AG Grid colors OK)",
                "status": "PASS",
                "detail": "from vizro.themes import ... detected",
            }
        )

    return checks


def check_spec3(project_dir: Path, custom_colors_requested: bool) -> list[dict]:
    """Check spec/3 for unexpected color_decisions when custom colors were not requested."""
    checks = []
    spec3_path = project_dir / "spec" / "3_visual_design.yaml"
    if not spec3_path.exists():
        checks.append(
            {
                "check": "spec/3 color_decisions absent",
                "status": "FAIL",
                "detail": "spec/3_visual_design.yaml not found",
            }
        )
        return checks

    try:
        data = yaml.safe_load(spec3_path.read_text())
    except yaml.YAMLError as e:
        checks.append({"check": "spec/3 valid YAML", "status": "FAIL", "detail": str(e)})
        return checks

    if not isinstance(data, dict):
        checks.append({"check": "spec/3 is a mapping", "status": "FAIL", "detail": "Root is not a dict"})
        return checks

    has_color_decisions = "color_decisions" in data
    if custom_colors_requested:
        checks.append(
            {
                "check": "spec/3 color_decisions (custom requested)",
                "status": "PASS",
                "detail": "Custom colors were requested; color_decisions is acceptable",
            }
        )
    elif has_color_decisions:
        checks.append(
            {
                "check": "spec/3 has no color_decisions",
                "status": "FAIL",
                "detail": "color_decisions found but custom colors were not requested",
            }
        )
    else:
        checks.append({"check": "spec/3 has no color_decisions", "status": "PASS", "detail": ""})

    return checks


def validate(project_dir: str, custom_colors_requested: bool = False) -> dict:
    """Validate Vizro color consistency across app.py and spec/3."""
    project = Path(project_dir)
    checks = []
    checks.extend(check_app_py(project))
    checks.extend(check_spec3(project, custom_colors_requested))

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {"criterion": "vizro_colors_consistent", "status": status, "checks": checks}


if __name__ == "__main__":
    if len(sys.argv) < 2:  # noqa: PLR2004
        print(f"Usage: {sys.argv[0]} <project_dir> [--custom-colors-requested]", file=sys.stderr)  # noqa: T201
        sys.exit(1)
    project_dir = sys.argv[1]
    custom_colors = "--custom-colors-requested" in sys.argv
    result = validate(project_dir, custom_colors)
    print(json.dumps(result, indent=2))  # noqa: T201
    sys.exit(0 if result["status"] == "PASS" else 1)
