import re

# File paths
CSS_FILE = "vizro-bootstrap.min.css"
OUTPUT_FILE = "colors.py"

# List of CSS variables to extract
variables = [
    '--bs-primary',
    '--bs-secondary',
    '--bs-tertiary-color',
    '--bs-border-color',
    '--bs-body-bg'
]

# Read the CSS content from the file
with open(CSS_FILE, 'r') as file:
    css_content = file.read()

# Function to extract the last two occurrences of a variable
def extract_last_two_occurrences(variable, content):
    pattern = re.compile(rf'{variable}:\s*([^;]+);')
    matches = pattern.findall(content)
    if len(matches) >= 2:
        return matches[-2].strip(), matches[-1].strip()
    return None, None

# Dictionary to store the extracted values
extracted_values = {}

# Extract the last two occurrences for each variable
for variable in variables:
    dark_value, light_value = extract_last_two_occurrences(variable, css_content)
    extracted_values[f'{variable[2:].upper()}-DARK'] = dark_value
    extracted_values[f'{variable[2:].upper()}-LIGHT'] = light_value

# Generate the Python file content
python_content = "BS_COLORS = {\n"
for key, value in extracted_values.items():
    python_content += f"'{key}': '{value}',\n"
python_content += "}"

# Write the content to the output Python file
with open(OUTPUT_FILE, 'w') as file:
    file.write(python_content.strip())

print(f"{OUTPUT_FILE} file has been created with the extracted values.")
