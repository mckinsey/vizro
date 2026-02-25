"""Utility functions for generating PyCafe links."""

import base64
import gzip
import json
import re
import textwrap
from dataclasses import dataclass
from urllib.parse import quote, urlencode

import requests
from github import Auth, Github
from github.Commit import Commit
from github.Repository import Repository
from playwright.sync_api import sync_playwright


# Function to extract version string from file content using regex
def _extract_version(content: str) -> str:
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if version_match:
        return version_match.group(1)
    return "unknown"


def fetch_package_versions(repo_name: str, commit_sha: str) -> tuple[str, str]:
    """Fetch package versions directly from the repository files.

    This function retrieves the version strings from the __init__.py files of vizro and vizro-ai
    packages for the specific commit being tested.

    Args:
        repo_name: Name of the GitHub repository
        commit_sha: The commit SHA to fetch versions from

    Returns:
        A tuple with (vizro_version, vizro_ai_version)
    """
    vizro_version = "unknown"
    vizro_ai_version = "unknown"

    # Define paths to __init__.py files that contain version information
    version_files = {"vizro": "vizro-core/src/vizro/__init__.py", "vizro-ai": "vizro-ai/src/vizro_ai/__init__.py"}

    # Fetch each file and extract the version
    for package, file_path in version_files.items():
        url = f"https://raw.githubusercontent.com/{repo_name}/{commit_sha}/{file_path}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            content = response.text

            # Update the appropriate version
            version = _extract_version(content)
            if package == "vizro" and version != "unknown":
                vizro_version = version
            elif package == "vizro-ai" and version != "unknown":
                vizro_ai_version = version

        except Exception as e:
            print(f"Failed to fetch version for {package}: {str(e)}")  # noqa

    return vizro_version, vizro_ai_version


@dataclass
class PyCafeConfig:
    """Configuration for PyCafe link generation."""

    github_token: str
    repo_name: str
    run_id: str
    commit_sha: str
    pr_number: int | None = None
    pycafe_url: str = "https://py.cafe"
    vizro_raw_url: str = "https://raw.githubusercontent.com/mckinsey/vizro"
    vizro_version: str = "unknown"
    vizro_ai_version: str = "unknown"


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
        f"vizro@{config.pycafe_url}/gh/artifact/mckinsey/vizro/actions/runs/{config.run_id}/"
        f"pip/vizro-{config.vizro_version}-py3-none-any.whl"
    )


def _get_vizro_ai_requirement(config: PyCafeConfig, use_latest_release: bool = False) -> str:
    """Get the Vizro AI requirement string for PyCafe."""
    if use_latest_release:
        return "vizro-ai"
    return (
        f"vizro-ai@{config.pycafe_url}/gh/artifact/mckinsey/vizro/actions/runs/{config.run_id}/"
        f"pip2/vizro_ai-{config.vizro_ai_version}-py3-none-any.whl"
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
    extra_requirements: list[str] | None = None,
    use_latest_release: bool = False,
) -> str:
    """Generate a PyCafe link for the example dashboard."""
    base_url = f"{config.vizro_raw_url}/{config.commit_sha}/{directory_path}"

    # Requirements - either use latest release or commit's wheel file
    requirements = []
    if directory_path.startswith("vizro-ai/"):
        # An example in this folder may require the latest vizro-ai and vizro-core releases
        requirements.extend(
            [_get_vizro_ai_requirement(config, use_latest_release), _get_vizro_requirement(config, use_latest_release)]
        )
    else:
        # All other examples do not require vizro-ai, but still the latest vizro-core release
        requirements.extend([_get_vizro_requirement(config, use_latest_release)])

    if extra_requirements:
        requirements.extend(extra_requirements)

    # App file - get current commit, and modify to remove if clause
    app_content = _fetch_app_content(base_url)

    # Get directory files
    folder_files = _fetch_directory_files(config, directory_path)

    # JSON object
    json_object = {
        "code": app_content,
        "requirements": "\n".join(requirements),
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
    config: PyCafeConfig, directory_path: str, extra_requirements: list[str] | None = None
) -> dict[str, str]:
    """Generate both commit and release links for comparison."""
    return {
        "commit": generate_link(config, directory_path, extra_requirements, use_latest_release=False),
        "release": generate_link(config, directory_path, extra_requirements, use_latest_release=True),
    }


def create_status_check(
    commit: Commit,
    directory: str,
    url: str,
    state: str = "success",
    description: str = "Test out the app live on PyCafe",
):
    """Create a GitHub status check for a PyCafe link."""
    context = f"PyCafe Example ({directory})"
    commit.create_status(state=state, target_url=url, description=description, context=context)
    print(f"Status created for {context} with URL: {url}")  # noqa


def get_example_directories() -> dict[str, list[str] | None]:
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
        "vizro-core/examples/tutorial/": None,
    }


def test_pycafe_link(url: str, wait_for_text: str | bool, wait_for_locator: str | bool) -> int:
    """Test if a PyCafe link loads and renders correctly.

    Return code is showing appropriate exit code.
    Success = 0, Failure = 1.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the page
            page.goto(url, timeout=60000)

            # Get the app frame and wait for title or element
            frame = page.frame_locator("#app")
            if wait_for_text:
                frame.get_by_text(wait_for_text).wait_for(timeout=90000)
            if wait_for_locator:
                frame.locator(wait_for_locator).wait_for(timeout=90000)

            print(f"✅ Successfully verified PyCafe link: {url}")  # noqa
            return 0

        except Exception as e:
            print(f"❌ Failed to verify PyCafe link: {url}")  # noqa
            print(f"Error: {str(e)}")  # noqa
            return 1

        finally:
            browser.close()
