"""Generate PyCafe links for the example dashboards and post them as a comment on the pull request and as status."""

import base64
import datetime
import gzip
import json
import sys
import textwrap
from pathlib import Path
from typing import Optional
from urllib.parse import quote, urlencode

from github import Auth, Github

GITHUB_TOKEN = sys.argv[1]
REPO_NAME = sys.argv[2]
PR_NUMBER = int(sys.argv[3])
RUN_ID = sys.argv[4]
COMMIT_SHA = sys.argv[5]
WHL_FILE = next(Path("dist").glob("*.whl")).name
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
pr = repo.get_pull(PR_NUMBER)
commit_sha_files = pr.head.sha
commit = repo.get_commit(COMMIT_SHA)


def generate_link(directory: str, extra_requirements: Optional[list[str]] = None):
    """Generate a PyCafe link for the example dashboards."""
    base_url = f"{VIZRO_RAW_URL}/{commit_sha_files}/vizro-core/{directory}"

    # Requirements
    requirements = "\n".join(
        [
            f"{PYCAFE_URL}/gh/artifact/mckinsey/vizro/actions/runs/{RUN_ID}/pip/{WHL_FILE}",
            *(extra_requirements or []),
        ],
    )

    # App file
    app_content = Path(directory, "app.py").read_text()
    app_content_split = app_content.split('if __name__ == "__main__":')
    if len(app_content_split) > 1:
        app_content = app_content_split[0] + textwrap.dedent(app_content_split[1])

    # JSON object
    json_object = {
        "code": app_content,
        "requirements": requirements,
        "files": [],
    }

    json_object["files"] = [
        {
            "name": str(file_path.relative_to(directory)),
            "url": f"{base_url}/{file_path.relative_to(directory).as_posix()}",
        }
        for file_path in Path(directory).rglob("*")
        if not file_path.is_dir() and file_path.relative_to(directory) != Path("app.py")
    ]

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
        "examples/dev/": ["openpyxl"],
        "examples/scratch_dev": None,
        "examples/visual-vocabulary/": ["autoflake==2.3.1", "black==24.4.2", "isort==5.13.2", "plotly==5.24.1"],
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
    post_comment(urls)
