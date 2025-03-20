"""Script to generate PyCafe links and create GitHub comments and status checks."""

import argparse
import datetime

from pycafe_utils import (
    PyCafeConfig,
    create_github_client,
    create_status_check,
    fetch_package_versions,
    generate_comparison_links,
    get_example_directories,
)


def post_comment(pr_object, config: PyCafeConfig, comparison_urls_dict: dict[str, dict[str, str]]):
    """Post a comment on the pull request with the PyCafe dashboard links."""
    template = """## View the example dashboards of the current commit live on PyCafe :coffee: :rocket:\n
Updated on: {current_utc_time}
Commit: {commit_sha}

Compare the examples using the commit's wheel file vs the latest released version:
{dashboards}
"""

    # Find existing comments by the bot
    comments = pr_object.get_issue_comments()
    bot_comment = None
    for comment in comments:
        if comment.body.startswith("## View the example dashboards of the current commit live"):
            bot_comment = comment
            break

    # Get current UTC datetime
    current_utc_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    # Format the comparison links
    dashboards = "\n\n".join(
        f"### {directory}\n"
        f"[View with commit's wheel]({urls['commit']}) vs [View with latest release]({urls['release']})"
        for directory, urls in comparison_urls_dict.items()
    )

    # Update the existing comment or create a new one
    comment_body = template.format(
        current_utc_time=current_utc_time,
        commit_sha=config.commit_sha,
        dashboards=dashboards,
    )

    if bot_comment:
        bot_comment.edit(comment_body)
        print("Comment updated on the pull request.")  # noqa
    else:
        pr_object.create_issue_comment(comment_body)
        print("Comment added to the pull request.")  # noqa


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PyCafe links for the example dashboards.")
    parser.add_argument("--github-token", required=True, help="GitHub token for authentication")
    parser.add_argument("--repo-name", required=True, help="Name of the GitHub repository")
    parser.add_argument("--run-id", required=True, help="GitHub Actions run ID")
    parser.add_argument("--commit-sha", required=True, help="Commit SHA")
    parser.add_argument("--pr-number", type=int, help="Pull request number (optional)")

    args = parser.parse_args()

    # Create configuration
    config = PyCafeConfig(
        github_token=args.github_token,
        repo_name=args.repo_name,
        run_id=args.run_id,
        commit_sha=args.commit_sha,
        pr_number=args.pr_number,
    )

    # Fetch package versions directly and update config
    try:
        config.package_version, config.vizro_ai_package_version = fetch_package_versions(
            config.repo_name, config.commit_sha
        )
    except Exception as e:
        print(f"Error fetching versions: {e}")  # noqa
        # Keep the default values if an error occurs

    # Initialize GitHub connection
    repo, commit = create_github_client(config)

    # Print package versions from the repository at the current commit
    print("Fetching package versions from repository...")  # noqa
    print(f"Vizro version from repo: {config.package_version}")  # noqa
    print(f"Vizro-AI version from repo: {config.vizro_ai_package_version}")  # noqa

    # Get example directories
    directories_with_requirements = get_example_directories()

    # Generate comparison links for each directory
    comparison_urls = {
        directory: generate_comparison_links(config, directory, extra_requirements)
        for directory, extra_requirements in directories_with_requirements.items()
    }

    # Create status for each URL - use the commit version for status
    for directory, urls in comparison_urls.items():
        create_status_check(commit, directory, urls["commit"])

    # Post the comment with the comparison links
    if config.pr_number is not None:
        pr = repo.get_pull(config.pr_number)
        post_comment(pr, config, comparison_urls)
