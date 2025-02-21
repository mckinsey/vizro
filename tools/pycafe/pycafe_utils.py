"""Utility functions for generating PyCafe links."""

import base64
import gzip
import json
import textwrap
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote, urlencode

import requests
import vizro
from github import Auth, Github
from github.Commit import Commit
from github.Repository import Repository


@dataclass
class PyCafeConfig:
    """Configuration for PyCafe link generation."""

    github_token: str
    repo_name: str
    run_id: str
    commit_sha: str
    pr_number: Optional[int] = None
    pycafe_url: str = "https://py.cafe"
    vizro_raw_url: str = "https://raw.githubusercontent.com/mckinsey/vizro"
    package_version: str = vizro.__version__


def create_github_client(config: PyCafeConfig) -> tuple[Repository, Commit]:
    """Create GitHub client and return repo and commit objects."""
    auth = Auth.Token(config.github_token)
    github = Github(auth=auth)
    repo = github.get_repo(config.repo_name)
    commit = repo.get_commit(config.commit_sha)
    return repo, commit


def _get_vizro_requirement(config: PyCafeConfig, use_latest_release: bool = False) -> str:
    """Get the Vizro requirement string for PyCafe."""
    if use_latest_release:
        return "vizro"
    return (
        f"{config.pycafe_url}/gh/artifact/mckinsey/vizro/actions/runs/{config.run_id}/"
        f"pip/vizro-{config.package_version}-py3-none-any.whl"
    )


def _fetch_app_content(base_url: str) -> str:
    """Fetch and process app.py content from the repository."""
    response = requests.get(f"{base_url}/app.py", timeout=10)
    response.raise_for_status()

    app_content = response.text
    app_content_split = app_content.split('if __name__ == "__main__":')
    if len(app_content_split) > 1:
        return app_content_split[0] + textwrap.dedent(app_content_split[1])
    return app_content


def _fetch_directory_files(config: PyCafeConfig, directory_path: str) -> list[dict]:
    """Fetch files in a directory from GitHub API."""
    url = f"https://api.github.com/repos/{config.repo_name}/git/trees/{config.commit_sha}?recursive=1"
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    files = response.json().get("tree", [])
    return [file for file in files if file["path"].startswith(directory_path)]


def generate_link(
    config: PyCafeConfig,
    directory_path: str,
    extra_requirements: Optional[list[str]] = None,
    use_latest_release: bool = False,
) -> str:
    """Generate a PyCafe link for the example dashboard."""
    base_url = f"{config.vizro_raw_url}/{config.commit_sha}/{directory_path}"

    # Requirements - either use latest release or commit's wheel file
    requirements = "\n".join(
        [
            _get_vizro_requirement(config, use_latest_release),
            *(extra_requirements or []),
        ]
    )

    # App file - get current commit, and modify to remove if clause
    app_content = _fetch_app_content(base_url)

    # Get directory files
    folder_files = _fetch_directory_files(config, directory_path)

    # JSON object
    json_object = {
        "code": app_content,
        "requirements": requirements,
        "files": [
            {
                "name": file["path"].removeprefix(f"{directory_path}"),
                "url": f"{base_url}{file['path'].removeprefix(f'{directory_path}')}",
            }
            for file in folder_files
            if file["type"] == "blob"
            and file["path"] not in {f"{directory_path}/app.py", f"{directory_path}/requirements.txt"}
        ],
    }

    json_text = json.dumps(json_object)
    compressed_json_text = gzip.compress(json_text.encode("utf8"))
    base64_text = base64.b64encode(compressed_json_text).decode("utf8")
    query = urlencode({"c": base64_text}, quote_via=quote)
    return f"{config.pycafe_url}/snippet/vizro/v1?{query}"


def generate_comparison_links(
    config: PyCafeConfig, directory_path: str, extra_requirements: Optional[list[str]] = None
) -> dict[str, str]:
    """Generate both commit and release links for comparison."""
    return {
        "commit": generate_link(config, directory_path, extra_requirements, use_latest_release=False),
        "release": generate_link(config, directory_path, extra_requirements, use_latest_release=True),
    }


def create_status_check(commit: Commit, directory: str, url: str, state: str = "success"):
    """Create a GitHub status check for a PyCafe link."""
    description = "Test out the app live on PyCafe"
    context = f"PyCafe Example ({directory})"
    commit.create_status(state=state, target_url=url, description=description, context=context)
    print(f"Status created for {context} with URL: {url}")  # noqa


def get_example_directories() -> dict[str, Optional[list[str]]]:
    """Return a dictionary of example directories and their requirements."""
    return {
        "vizro-core/examples/scratch_dev": None,
        "vizro-core/examples/dev/": ["openpyxl"],
        "vizro-core/examples/visual-vocabulary/": [
            "autoflake==2.3.1",
            "black==24.4.2",
            "isort==5.13.2",
            "plotly==5.24.1",
        ],
        "vizro-ai/examples/dashboard_ui/": [
            "vizro-ai>=0.3.0",
            "black",
            "openpyxl",
            "langchain_anthropic",
            "langchain_mistralai",
            "greenlet # mock",
            "tiktoken @ https://py.cafe/files/maartenbreddels/tiktoken-demo/tiktoken-0.7.0-cp312-cp312-pyodide_2024_0_wasm32.whl",
            "https://py.cafe/files/maartenbreddels/jiter-demo/jiter-0.6.1-cp312-cp312-pyodide_2024_0_wasm32.whl",
            "https://py.cafe/files/maartenbreddels/tokenizers-demo/tokenizers-0.20.2.dev0-cp312-cp312-pyodide_2024_0_wasm32.whl",
        ],
    }
