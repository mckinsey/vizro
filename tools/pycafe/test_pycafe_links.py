"""Script to test PyCafe links using Playwright."""

import argparse
import sys

from playwright.sync_api import sync_playwright
from pycafe_utils import (
    PyCafeConfig,
    create_github_client,
    create_status_check,
    generate_link,
)


def test_pycafe_link(url: str, wait_for_text: str):
    """Test if a PyCafe link loads and renders correctly."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the page and wait for network to be idle
            page.goto(url, wait_until="networkidle")

            # Get the app frame and wait for title
            frame = page.frame_locator("#app")
            frame.get_by_text(wait_for_text).wait_for()

            print(f"✅ Successfully verified PyCafe link: {url}")  # noqa
            return True

        except Exception as e:
            print(f"❌ Failed to verify PyCafe link: {url}")  # noqa
            print(f"Error: {str(e)}")  # noqa
            page.screenshot(path="pycafe_error.png")
            return False

        finally:
            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test PyCafe links for the example dashboards.")
    parser.add_argument("--github-token", required=True, help="GitHub token for authentication")
    parser.add_argument("--repo-name", required=True, help="Name of the GitHub repository")
    parser.add_argument("--run-id", required=True, help="GitHub Actions run ID")
    parser.add_argument("--commit-sha", required=True, help="Commit SHA")

    args = parser.parse_args()

    # Create configuration
    config = PyCafeConfig(
        github_token=args.github_token,
        repo_name=args.repo_name,
        run_id=args.run_id,
        commit_sha=args.commit_sha,
    )

    # Initialize GitHub connection
    repo, commit = create_github_client(config)

    # Test dev example with latest version - we currently one test this for simplicity, but this could be changed
    # This would mean that we need to change also what the wait_for_text is
    dev_directory = "vizro-core/examples/dev/"
    extra_requirements = ["openpyxl"]
    url_generated = generate_link(config, dev_directory, extra_requirements, use_latest_release=False)

    # Test the link
    success = test_pycafe_link(url=url_generated, wait_for_text="Vizro Features")

    # Only create a status check if the test fails. On success, the status check will be created
    # by the create_pycafe_links_comments.py script when it posts the comment.
    # Dummy
    if not success:
        create_status_check(commit, dev_directory, url_generated, state="failure")

    # Exit with appropriate status code
    sys.exit(0 if success else 1)
