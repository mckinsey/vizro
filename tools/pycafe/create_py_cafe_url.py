import base64
import gzip
import json
import os
from urllib.parse import quote, urlencode

COMMIT_HASH = "3321df6426357e7472303a3ed0b887b80349bc0d"


def generate_link():
    base_url = f"https://raw.githubusercontent.com/mckinsey/vizro/{COMMIT_HASH}/tools/pycafe/"
    json_object = {"code": f"{base_url}app.py", "requirements": f"{base_url}requirements.txt", "files": []}

    # directory = "../../vizro-core/examples/scratch_dev"
    # for root, _, files in os.walk(directory):
    #     print(root)
    print(os.getcwd())
    directory = "vizro/tools/pycafe"
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
    print(generate_link())
# Example usage
# print(generate_link())
