import base64
import gzip
import json
import os
import textwrap
from urllib.parse import quote, urlencode

COMMIT_HASH = str(os.getenv("COMMIT_HASH"))
COMMIT_HASH = "16563957afa641c4141752099acff2a8049fd63c"
print(COMMIT_HASH)


def generate_link(directory):
    base_url = f"https://raw.githubusercontent.com/mckinsey/vizro/{COMMIT_HASH}/{directory.lstrip('./')}"

    app_file_path = os.path.join(directory, "app.py")
    with open(app_file_path, "r") as app_file:
        app_content = app_file.read()
        app_content_split = app_content.split('if __name__ == "__main__":')
        app_content = app_content_split[0] + textwrap.dedent(app_content_split[1])
        # print(app_content)
        # print("=====")

    json_object = {
#         "code": """import vizro.plotly.express as px
# from vizro import Vizro
# import vizro.models as vm

# df = px.data.iris()

# page = vm.Page(
#     title="My first dashboard",
#     components=[
#         vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
#         vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species")),
#     ],
#     controls=[
#         vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
#     ],
# )

# dashboard = vm.Dashboard(pages=[page])
# Vizro().build(dashboard).run()""", 
        "code": str(app_content),
        "requirements": "https://py.cafe/gh/artifact/mckinsey/vizro/2054307112/vizro-0.1.25.dev0-py3-none-any.whl",
        "files": [],
    }
    # print("=====")
    for root, _, files in os.walk(directory):
        for file in files:
            print(root, file)
            if "yaml" in root or "app.py" in file:
                continue
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            file_url = f"{base_url}{relative_path.replace(os.sep, '/')}"
            json_object["files"].append({"name": relative_path, "url": file_url})
            # Add detailed logging
            print(f"Added file: {relative_path}, URL: {file_url}")
            print(f"Current JSON object: {json.dumps(json_object, indent=2)}")
            print("-+-")

    # Final JSON object logging
    # print(f"Final JSON object: {json.dumps(json_object, indent=2)}")
    print("******")
    print(json_object["code"])
    print("---")
    # print(json_object["files"])
    # print("---")
    # print(json_object["requirements"])
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
