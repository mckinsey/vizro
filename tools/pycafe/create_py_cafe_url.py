import base64
import gzip
import json
import os
import textwrap
from urllib.parse import quote, urlencode

COMMIT_HASH = "a67e87527430c613fdebda66a90f433398c707dd"


def generate_link(directory):
    base_url = f"https://raw.githubusercontent.com/mckinsey/vizro/{COMMIT_HASH}/{directory.lstrip('./')}"

    app_file_path = os.path.join(directory, "app.py")
    with open(app_file_path, "r") as app_file:
        app_content = app_file.read()
        app_content_split = app_content.split('if __name__ == "__main__":')
        app_content = app_content_split[0] + textwrap.dedent(app_content_split[1])

    json_object = {"code": app_content, "requirements": "vizro>=0.1.24", "files": []}

    for root, _, files in os.walk(directory):
        for file in files:
            print(root, file)
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            file_url = f"{base_url}{relative_path.replace(os.sep, '/')}"
            json_object["files"].append({"name": relative_path, "url": file_url})
    print(json_object)
    json_text = json.dumps(json_object)
    compressed_json_text = gzip.compress(json_text.encode("utf8"))
    base64_text = base64.b64encode(compressed_json_text).decode("utf8")
    query = urlencode({"c": base64_text}, quote_via=quote)
    base_url = "https://py.cafe"
    return f"{base_url}/snippet/vizro/v1?{query}"


if __name__ == "__main__":
    print("=========")
    print(os.getcwd())
    directory = "./vizro-core/examples/scratch_dev/"
    # directory = "./tools/pycafe"
    print(generate_link(directory=directory))
# Example usage
# print(generate_link())