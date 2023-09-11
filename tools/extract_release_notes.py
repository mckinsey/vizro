import sys


def extract_section(filename, heading):
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
    section = "".join(lines[start_line + 1 : end_line]).strip()
    return section


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception("Usage: python extract_release_notes.py <filename> <heading>")

    filename = sys.argv[1]
    heading = sys.argv[2]
    section = extract_section(filename, heading)

    if not section:
        raise Exception(f"Section not found under the {heading} heading")
    with open("release_body.txt", "w") as text_file:
        text_file.write(section)
