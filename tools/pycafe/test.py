import os
import sys

from github import Github

# Authenticate with GitHub
access_token = os.getenv("GITHUB_TOKEN")
g = Github(access_token)

# for repo in g.get_user().get_repos():
#     print(repo.name)

print(sys.argv)
repo = sys.argv[1]
pr = sys.argv[2]
# type = sys.argv[3]
# code = sys.argv[4]
# requirements = sys.argv[5]

# Get the repository
repo = g.get_repo(repo)

# Get the pull request
pr_number = int(pr)
pr = repo.get_pull(pr_number)
print(pr)

# base_url = f"https://py.cafe/snippet/{type}/v1"
url = "https://py.cafe/snippet/vizro/v1"  # f"{base_url}#code={quote(code)}&requirements={quote(requirements)}"

# # Get the latest commit SHA from the PR
if 1:
    commit_sha = pr.head.sha
    print(commit_sha)

    # Define the deployment status
    state = "success"  # Options: 'error', 'failure', 'pending', 'success'
    description = "Test out this PR on a PyCafe environment"
    context = "PyCafe"

    # Create the status on the commit
    commit = repo.get_commit(commit_sha)
    commit.create_status(state=state, target_url=url, description=description, context=context)
    print(f"Deployment status added to commit {commit_sha}")
