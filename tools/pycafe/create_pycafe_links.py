"""Generate PyCafe links for the example dashboards and post them as a comment on the pull request and as status."""

import argparse
import base64
import datetime
import gzip
import json
import textwrap
from typing import Optional
from urllib.parse import quote, urlencode

import requests
import vizro
from github import Auth, Github

PACKAGE_VERSION = vizro.__version__

# Parse arguments
parser = argparse.ArgumentParser(description="Generate PyCafe links for the example dashboards.")
parser.add_argument("--github-token", required=True, help="GitHub token for authentication")
parser.add_argument("--repo-name", required=True, help="Name of the GitHub repository")
parser.add_argument("--run-id", required=True, help="GitHub Actions run ID")
parser.add_argument("--commit-sha", required=True, help="Commit SHA")
parser.add_argument("--pr-number", type=int, help="Pull request number (optional)")


args = parser.parse_args()

GITHUB_TOKEN = args.github_token
REPO_NAME = args.repo_name
PR_NUMBER = args.pr_number
RUN_ID = args.run_id
COMMIT_SHA = args.commit_sha
PYCAFE_URL = "https://py.cafe"
VIZRO_RAW_URL = "https://raw.githubusercontent.com/mckinsey/vizro"

BOT_COMMENT_TEMPLATE = """## View the example dashboards of the current commit live on PyCafe :coffee: :rocket:\n
Updated on: {current_utc_time}
Commit: {commit_sha}

{dashboards}
"""

# Access
auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)

# Get PR and commits
repo = g.get_repo(REPO_NAME)
commit = repo.get_commit(COMMIT_SHA)


def generate_link(directory: str, extra_requirements: Optional[list[str]] = None):
    """Generate a PyCafe link for the example dashboards."""
    base_url = f"{VIZRO_RAW_URL}/{COMMIT_SHA}/{directory}"

    # Requirements
    requirements = "\n".join(
        [
            f"{PYCAFE_URL}/gh/artifact/mckinsey/vizro/actions/runs/{RUN_ID}/pip/vizro-{PACKAGE_VERSION}-py3-none-any.whl",
            *(extra_requirements or []),
        ]
    )

    # App file - get current commit, and modify to remove if clause
    app_content = requests.get(f"{base_url}/app.py", timeout=10).text
    app_content_split = app_content.split('if __name__ == "__main__":')
    if len(app_content_split) > 1:
        app_content = app_content_split[0] + textwrap.dedent(app_content_split[1])

    # JSON object
    json_object = {
        "code": app_content,
        "requirements": requirements,
        "files": [],
    }

    # GitHub API URL for a specific commit
    url = f"https://api.github.com/repos/{REPO_NAME}/git/trees/{COMMIT_SHA}?recursive=1"

    # Make the request to get all the files in the commit
    response = requests.get(url, timeout=20)
    if response.status_code == 200:  # noqa
        # Get the JSON response with the file tree
        files = response.json().get("tree", [])
        # Filter files for the specific folder path
        folder_files = [file for file in files if file["path"].startswith(directory)]

        # Add files to the json_object
        json_object["files"] = [
            {
                "name": file["path"].removeprefix(f"{directory}"),
                "url": f"{base_url}{file['path'].removeprefix(f'{directory}')}",
            }
            for file in folder_files
            # Filter out app.py and requirements.txt (as already added above)
            if file["type"] == "blob" and file["path"] not in {f"{directory}/app.py", f"{directory}/requirements.txt"}
        ]
    else:
        raise Exception(f"Failed to fetch file tree from GitHub API: {response.status_code} {response.text}")

    json_text = json.dumps(json_object)
    compressed_json_text = gzip.compress(json_text.encode("utf8"))
    base64_text = base64.b64encode(compressed_json_text).decode("utf8")
    query = urlencode({"c": base64_text}, quote_via=quote)
    return f"{PYCAFE_URL}/snippet/vizro/v1?{query}"


def post_comment(urls: dict[str, str]):
    """Post a comment on the pull request with the links to the PyCafe dashboards."""
    # Inspired by https://github.com/snehilvj/dash-mantine-components

    # Find existing comments by the bot
    comments = pr.get_issue_comments()
    bot_comment = None
    for comment in comments:
        if comment.body.startswith("## View the example dashboards of the current commit live"):
            bot_comment = comment
            break

    # Get current UTC datetime
    current_utc_time = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Define the comment body with datetime
    dashboards = "\n\n".join(f"Link: [{directory}]({url})" for directory, url in urls.items())

    # Update the existing comment or create a new one
    if bot_comment:
        bot_comment.edit(
            BOT_COMMENT_TEMPLATE.format(current_utc_time=current_utc_time, commit_sha=COMMIT_SHA, dashboards=dashboards)
        )
        print("Comment updated on the pull request.")  # noqa
    else:
        pr.create_issue_comment(
            BOT_COMMENT_TEMPLATE.format(current_utc_time=current_utc_time, commit_sha=COMMIT_SHA, dashboards=dashboards)
        )
        print("Comment added to the pull request.")  # noqa


if __name__ == "__main__":
    directories_with_requirements = {
        "vizro-core/examples/dev/": ["openpyxl"],
        "vizro-core/examples/scratch_dev": None,
        "vizro-core/examples/visual-vocabulary/": [
            "autoflake==2.3.1",
            "black==24.4.2",
            "isort==5.13.2",
            "plotly==5.24.1",
        ],
    }
    urls = {
        directory: generate_link(directory, extra_requirements)
        for directory, extra_requirements in directories_with_requirements.items()
    }

    # Create status
    for directory, url in urls.items():
        # Define the deployment status
        state = "success"  # Options: 'error', 'failure', 'pending', 'success'
        description = "Test out the app live on PyCafe"
        context = f"PyCafe Example ({directory})"

        # Create the status on the commit
        commit.create_status(state=state, target_url=url, description=description, context=context)
        print(f"Status created for {context} with URL: {url}")  # noqa

    # Post the comment with the links
    if PR_NUMBER is not None:
        pr = repo.get_pull(PR_NUMBER)
        post_comment(urls)

# Try out if this sticks with the local files that have just been changed. Add some files to scratch dev
