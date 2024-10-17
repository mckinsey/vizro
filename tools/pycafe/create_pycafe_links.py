"""Generate PyCafe links for the example dashboards and post them as a comment on the pull request and as status."""

import base64
import datetime
import gzip
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Optional
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


def generate_link(directory: str, extra_requirements: Optional[list[str]] = None):
    base_url = f"https://raw.githubusercontent.com/mckinsey/vizro/{commit_sha}/vizro-core/{directory}"

    # Requirements
    if extra_requirements:
        extra_requirements_concat: str = "\n".join(extra_requirements)
    else:
        extra_requirements_concat = ""
    requirements = (
        f"""{PYCAFE_URL}/gh/artifact/mckinsey/vizro/actions/runs/{RUN_ID}/pip/vizro-{PACKAGE_VERSION}-py3-none-any.whl\n"""
        + extra_requirements_concat
    )
    print(f"Requirements: {requirements}")

    # App file
    app_file_path = os.path.join(directory, "app.py")
    app_content = Path(app_file_path).read_text()
    app_content_split = app_content.split('if __name__ == "__main__":')
    app_content = app_content_split[0] + textwrap.dedent(app_content_split[1])

    # JSON object
    json_object = {
        "code": str(app_content),
        "requirements": requirements,
        "files": [],
    }
    for root, _, files in os.walk("./" + directory):
        for file in files:
            # print(root, file)
            if "app.py" in file:
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


def post_comment(urls: list[tuple[str, str]]):
    """Post a comment on the pull request with the links to the PyCafe dashboards."""
    # Inspired by https://github.com/snehilvj/dash-mantine-components

    # Find existing comments by the bot
    comments = pr.get_issue_comments()
    bot_comment = None
    for comment in comments:
        if comment.body.startswith("View the dashboard live on PyCafe:"):
            bot_comment = comment
            break

    # Get current UTC datetime
    current_utc_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Define the comment body with datetime
    dashboards = "\n\n".join(f"Link: [{directory}]({url})" for url, directory in urls)

    comment_body = f"""View the example dashboards of the current commit live on PyCafe:\n
Updated on: {current_utc_time}
Commit: {commit_sha}

{dashboards}
"""

    # Update the existing comment or create a new one
    if bot_comment:
        bot_comment.edit(comment_body)
        print("Comment updated on the pull request.")
    else:
        pr.create_issue_comment(comment_body)
        print("Comment added to the pull request.")


if __name__ == "__main__":
    urls = []

    # Generate links for each directory and create status
    for directory in sys.argv[1:]:
        if directory == "examples/dev/":
            url = generate_link(directory=directory, extra_requirements=["openpyxl"])
        else:
            url = generate_link(directory=directory)
        urls.append((url, directory))

        # Define the deployment status
        state = "success"  # Options: 'error', 'failure', 'pending', 'success'
        description = "Test out the app live on PyCafe"
        context = f"PyCafe Example ({directory})"

        # Create the status on the commit
        commit.create_status(state=state, target_url=url, description=description, context=context)

    # Post the comment with the links
    post_comment(urls)

    print("All done!")
