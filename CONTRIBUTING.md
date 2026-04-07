# Contributing to REPYS 2.0

Thanks for contributing.

## Development Setup

1. Create a Python 3.12 virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run tests before opening a pull request.

## Branch and Commit Rules

- Use short, focused branches.
- Keep commits atomic and descriptive.
- Reference issue numbers in commit messages when relevant.

## Code Standards

- Follow project architecture: UI -> Service -> Repository -> Database.
- Keep SQL inside repository classes only.
- Keep business rules in service layer.
- Use shared UI components and theme tokens.
- Add or update tests for every service-level change.

## Pull Request Checklist

- [ ] Tests pass locally
- [ ] New behavior has tests
- [ ] No unrelated refactoring included
- [ ] Documentation updated when needed
- [ ] Screenshots added for UI changes

## Reporting Bugs

Open an issue using the bug template and include:

- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details
