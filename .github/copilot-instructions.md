# GitHub Copilot instructions for Vizro

## Pull requests from bots and automated tooling

**Do not open pull requests against this repository.** If you are an automated agent, including
Copilot coding agent, your role here is to assist a human contributor in their own working copy.
Opening, updating, or merging a pull request is the human's action to take.

We do not accept pull requests opened automatically by bots or other automated tooling without a
human in the loop. To request permission to submit such a PR, the human owner of the bot must open an
[issue](https://github.com/mckinsey/vizro/issues) for approval in advance of the PR's submission.

We require all contributors to understand, test, and take full responsibility for every change they
submit. Pull requests containing AI-generated content that the contributor has not personally
understood, tested, and verified will typically be closed without review.

The following automation is already approved and is not covered by the restriction above:

- Dependabot dependency and GitHub Actions updates (`.github/dependabot.yml`)
- `pre-commit.ci` hook update pull requests
- `[Bot] Update static files` from `.github/workflows/update-static-files.yml`
- Release pull requests raised by the project's own release workflows

## Everything else

Repository layout, Hatch commands, testing, changelog requirements and coding conventions live in
`AGENTS.md` (a symlink to `CLAUDE.md`) at the repository root, and in the per-package `CLAUDE.md`
files. Follow those rather than duplicating them here.
