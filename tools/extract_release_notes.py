"""Extracts latest release notes from CHANGELOG.md and saves to file."""
import sys

from werkzeug.utils import secure_filename

ARG_NUM = 3


def _extract_section(filename, heading):
    with open(filename, "r") as file:
        lines = file.readlines()

    start_line, end_line = None, None

    for i, line in enumerate(lines):
        if line.startswith("# "):
            current_heading = line.strip("#").replace(":", "").strip()
            if current_heading == heading:
                start_line = i
            elif start_line is not None:
                end_line = i
                break

    if start_line is None:
        return None

    end_line = end_line or len(lines)
    section_out = "".join(lines[start_line + 1 : end_line]).strip()
    return section_out


if __name__ == "__main__":
    if len(sys.argv) != ARG_NUM:
        raise TypeError("Usage: python extract_release_notes.py <filename> <package_name>")

    PACKAGE_NAME = secure_filename(str(sys.argv[1]))
    FILE_NAME = PACKAGE_NAME + "/CHANGELOG.md"
    HEADING = sys.argv[2]

    section = _extract_section(FILE_NAME, HEADING)

    if not section:
        raise ValueError(f"Section not found under the {HEADING} heading")
    with open("release_body.txt", "w") as text_file:
        text_file.write(section)
