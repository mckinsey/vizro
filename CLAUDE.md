# Vizro Development Guide for AI Agents

This is a monorepo containing multiple Vizro packages. The main packages are:

- `vizro-core/`: The core Vizro dashboard framework
- `vizro-ai/`: Framework for AI-assisted dashboard development
- `vizro-mcp/`: Model Context Protocol server for AI-assisted dashboard development

## Development Setup (across all packages)

### Only Dependency: Hatch

Vizro uses [Hatch](https://hatch.pypa.io/) as its only direct development dependency. You don't need to manually install Python or create virtual environments - Hatch handles this automatically. If not installed, guide the user on how to install it.

### Working Directory

Navigate to the specific package directory (e.g., `cd vizro-core`) before running Hatch commands.

### Common Hatch Commands across all packages

Run these from within the package directory (e.g., `vizro-core/`):

- `hatch run pypath` - Show Python interpreter path
- `hatch run lint` - Check and fix code quality/formatting
- `hatch run changelog:add` - Generate changelog fragment (required for PRs)
- `hatch run test-unit` - Run test suite
- `hatch run docs:serve` - Build and serve documentation (hot-reloads)

## Development Flow

1. Make changes to code
1. Run `hatch run lint` to check formatting
1. Run `hatch run test-unit` to verify tests pass (you can add --last-failed to rerun only failures from the last test run)
1. Run `hatch run changelog:add` to create changelog fragment

## Key configuration files

- `pyproject.toml`: Main tooling configuration for the monorepo
