"""Script to test PyCafe links using Playwright."""

import argparse
import sys

from pycafe_utils import (
    PyCafeConfig,
    create_github_client,
    create_status_check,
    fetch_package_versions,
    generate_link,
    test_pycafe_link,
)

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

    # Fetch package versions directly and update config
    try:
        config.vizro_version, config.vizro_ai_version = fetch_package_versions(config.repo_name, config.commit_sha)
    except Exception as e:
        print(f"Error fetching versions: {e}")  # noqa
        # Keep the default values if an error occurs

    # Initialize GitHub connection
    repo, commit = create_github_client(config)

    # Print package versions from the repository at the current commit
    print("Fetching package versions from repository...")  # noqa
    print(f"Vizro version from repo: {config.vizro_version}")  # noqa
    print(f"Vizro-AI version from repo: {config.vizro_ai_version}")  # noqa

    # Test dev example with latest version - we currently one test this for simplicity, but this could be changed
    # This would mean that we need to change also what the wait_for_text is
    dev_directory = "vizro-core/examples/dev/"
    extra_requirements = ["openpyxl"]
    url_generated = generate_link(config, dev_directory, extra_requirements, use_latest_release=False)

    # Test the link
    exit_code = test_pycafe_link(url=url_generated, wait_for_text="Vizro Features", wait_for_locator=False)

    # Only create a status check if the test fails. On success, the status check will be created
    # by the create_pycafe_links_comments.py script when it posts the comment.
    if exit_code == 1:
        create_status_check(
            commit,
            dev_directory,
            url_generated,
            state="failure",
            description="Check if PyCafe links load properly (using vizro-core dev example)",
        )

    # Exit with appropriate status code
    sys.exit(exit_code)
