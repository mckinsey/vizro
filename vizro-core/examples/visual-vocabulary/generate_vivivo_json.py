"""Generate visual vocabulary JSON from vivivo directory."""

import importlib
import json
import re
from pathlib import Path

import vizro.models as vm
from chart_groups import CHART_GROUPS


def extract_card_text_sections(text):
    """Extract 'What is' and 'When should I use it' sections from card text."""
    what_pattern = r"#### What is .*?\?\s+(.*?)(?=####|$)"
    when_pattern = r"#### When should I use it\??\s+(.*?)(?=$)"

    what_match = re.search(what_pattern, text, re.DOTALL)
    when_match = re.search(when_pattern, text, re.DOTALL)

    what_text = what_match.group(1).strip() if what_match else ""
    when_text = when_match.group(1).strip() if when_match else ""

    # Clean up HTML elements and trailing non-breaking spaces
    what_text = re.sub(r"\n\s*&nbsp;\s*$", "", what_text)

    return what_text, when_text


def get_example_code(var_name, group_name=None):
    """Get the example code for a chart type."""
    script_dir = Path(__file__).resolve().parent
    examples_dir = script_dir / "pages" / "examples"

    possible_files = [
        f"{group_name}_{var_name}.py",  # e.g., time_column.py
        f"{var_name}.py",  # e.g., column.py
    ]

    for filename in possible_files:
        example_file = examples_dir / filename
        if example_file.exists():
            return example_file.read_text()

    return ""


def get_chart_name_from_example(var_name, group_name=None):
    """Get the chart name from the example file."""
    if group_name and var_name.startswith(f"{group_name}_"):
        return var_name[len(group_name) + 1 :]
    return var_name


def generate_visual_vocabulary():
    """Generate the visual vocabulary JSON file."""
    chart_groups = {}

    for chart_group in CHART_GROUPS:
        group_name = chart_group.name.lower().replace(" ", "_").replace("-", "_")

        chart_groups[group_name] = {
            "display_name": chart_group.name,
            "description": chart_group.intro_text.strip(),
            "charts": [],
        }

        try:
            module = importlib.import_module(f"pages.{group_name}")

            for page_info in chart_group.pages:
                var_name = page_info.title.lower().replace(" ", "_").replace("-", "_")
                page_var = f"{var_name}_page"
                if not hasattr(module, page_var):
                    continue

                page = getattr(module, page_var)

                card_text = ""
                for component in page.components:
                    if isinstance(component, vm.Card):
                        card_text = component.text
                        break

                what_text, when_text = extract_card_text_sections(card_text)

                code = get_example_code(var_name, group_name)
                chart_name = get_chart_name_from_example(var_name, group_name)

                chart_info = {
                    "chart_name": chart_name,
                    "definition": what_text,
                    "when_to_use": when_text,
                    "example_code": code,
                }

                chart_groups[group_name]["charts"].append(chart_info)
        except ImportError as e:
            raise ImportError(f"Error importing module for {group_name}: {e}")

    visual_vocabulary = {"chart_groups": chart_groups}

    output_path = Path(__file__).resolve().parent / "visual_vocabulary.json"

    output_path.write_text(json.dumps(visual_vocabulary, indent=2))

    return visual_vocabulary


if __name__ == "__main__":
    generate_visual_vocabulary()
