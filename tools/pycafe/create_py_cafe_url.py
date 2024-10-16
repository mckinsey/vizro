import base64
import gzip
import json
import os
import subprocess
import textwrap
from pathlib import Path
from urllib.parse import quote, urlencode
import sys

COMMIT_HASH = str(os.getenv("COMMIT_HASH"))
RUN_ID = str(os.getenv("RUN_ID"))
PACKAGE_VERSION = subprocess.check_output(["hatch", "version"], cwd="vizro-core").decode("utf-8").strip()
PYCAFE_URL = "https://py.cafe"


def generate_link(directory):
    base_url = f"https://raw.githubusercontent.com/mckinsey/vizro/{COMMIT_HASH}/{directory}"

    app_file_path = os.path.join(directory, "app.py")
    app_content = Path(app_file_path).read_text()
    app_content_split = app_content.split('if __name__ == "__main__":')
    app_content = app_content_split[0] + textwrap.dedent(app_content_split[1]) 

    json_object = {
        "code": str(app_content),
        "requirements": f"{PYCAFE_URL}/gh/artifact/mckinsey/vizro/actions/runs/{RUN_ID}/pip/vizro-{PACKAGE_VERSION}-py3-none-any.whl",
        "files": [],
    }
    for root, _, files in os.walk("./"+directory):
        for file in files:
            # print(root, file)
            if "yaml" in root or "app.py" in file:
                continue
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            file_url = f"{base_url}{relative_path.replace(os.sep, '/')}"
            json_object["files"].append({"name": relative_path, "url": file_url})

    # Final JSON object logging
    print(f"Final JSON object: {json.dumps(json_object, indent=2)}")

    json_text = json.dumps(json_object)
    compressed_json_text = gzip.compress(json_text.encode("utf8"))
    base64_text = base64.b64encode(compressed_json_text).decode("utf8")
    query = urlencode({"c": base64_text}, quote_via=quote)
    return f"{PYCAFE_URL}/snippet/vizro/v1?{query}"


if __name__ == "__main__":
    directory = "vizro-core/examples/scratch_dev/"
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    print(generate_link(directory=directory))