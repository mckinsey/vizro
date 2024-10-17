import base64
import gzip
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from urllib.parse import quote, urlencode

from github import Auth, Github

GITHUB_TOKEN = str(os.getenv("GITHUB_TOKEN"))
REPO_NAME = str(os.getenv("GITHUB_REPOSITORY"))
PR_NUMBER = int(os.getenv("PR_NUMBER"))


RUN_ID = str(os.getenv("RUN_ID"))
PACKAGE_VERSION = subprocess.check_output(["hatch", "version"]).decode("utf-8").strip()
PYCAFE_URL = "https://py.cafe"

# Access
auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)

# Get PR and commits
repo = g.get_repo(REPO_NAME)
pr = repo.get_pull(PR_NUMBER)
commit_sha = pr.head.sha
commit = repo.get_commit(commit_sha)


def generate_link(directory):
    base_url = f"https://raw.githubusercontent.com/mckinsey/vizro/{commit_sha}/vizro-core/{directory}"

    app_file_path = os.path.join(directory, "app.py")
    app_content = Path(app_file_path).read_text()
    app_content_split = app_content.split('if __name__ == "__main__":')
    app_content = app_content_split[0] + textwrap.dedent(app_content_split[1])

    json_object = {
        "code": str(app_content),
        "requirements": f"{PYCAFE_URL}/gh/artifact/mckinsey/vizro/actions/runs/{RUN_ID}/pip/vizro-{PACKAGE_VERSION}-py3-none-any.whl",
        "files": [],
    }
    for root, _, files in os.walk("./" + directory):
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


urls = [(generate_link(directory=directory), directory) for directory in sys.argv[1:]]

for url, directory in urls:
    # print(f"Generating PyCafe URL for directory: {directory}")
    # url = generate_link(directory=directory)
    # pr.create_issue_comment("Foo bar")

    # Define the deployment status
    state = "success"  # Options: 'error', 'failure', 'pending', 'success'
    description = "Test out the app live on PyCafe"
    context = f"PyCafe Example ({directory})"

    # Create the status on the commit
    commit.create_status(state=state, target_url=url, description=description, context=context)
    # print(f"Deployment status added to commit {COMMIT_SHA}")
