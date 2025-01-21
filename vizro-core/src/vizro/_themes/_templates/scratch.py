import re

# File paths
CSS_FILE = "vizro-bootstrap.min.css"
OUTPUT_FILE = "colors.py"

# List of CSS variables to extract
VARIABLES = [
    '--bs-primary',
    '--bs-secondary',
    '--bs-tertiary-color',
    '--bs-border-color',
    '--bs-body-bg'
]


def read_css_file(file_path):
    """Read the CSS content from the specified file."""
    with open(file_path, 'r') as file:
        return file.read()

def extract_last_two_occurrences(variable, content):
    """Extract the last two occurrences of a variable from the CSS content."""
    pattern = re.compile(rf'{variable}:\s*([^;]+);')
    matches = pattern.findall(content)
    if len(matches) >= 2:
        return matches[-2].strip(), matches[-1].strip()
    return None, None


def extract_values(variables, content):
    """Extract the last two occurrences for each variable in the list."""
    extracted_values = {}
    for variable in variables:
        dark_value, light_value = extract_last_two_occurrences(variable, content)
        extracted_values[f'{variable[2:].upper()}-DARK'] = dark_value
        extracted_values[f'{variable[2:].upper()}-LIGHT'] = light_value
    return extracted_values


def generate_python_content(extracted_values):
    """Generate the Python file content from the extracted values."""
    python_content = "BS_COLORS = {\n"
    for key, value in extracted_values.items():
        python_content += f"'{key}': '{value}',\n"
    python_content += "}"
    return python_content


def write_python_file(file_path, content):
    """Write the generated content to the specified Python file."""
    with open(file_path, 'w') as file:
        file.write(content.strip())


def main():
    # Read the CSS content from the file
    css_content = read_css_file(CSS_FILE)

    # Extract the values
    extracted_values = extract_values(VARIABLES, css_content)

    # Generate the Python file content
    python_content = generate_python_content(extracted_values)

    # Write the content to the output Python file
    write_python_file(OUTPUT_FILE, python_content)

    print(f"{OUTPUT_FILE} file has been created with the extracted values.")


if __name__ == "__main__":
    main()
