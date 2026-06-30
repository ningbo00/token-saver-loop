# Contributing

Thanks for helping improve Token Saver Loop. The project is intentionally portable and lightweight, so the best contributions usually make the workflow clearer, safer, or easier to try.

## Good First Contributions

- Fix unclear README or beginner-guide wording.
- Improve examples that show real reviewer/worker handoffs.
- Report friction from trying the portable kit in another project.
- Add focused tests for helper behavior.
- Improve Windows-first copy/run instructions without adding install complexity.

## Project Direction

Token Saver Loop is portable-first:

- The main workflow is copying `portable/token-saver-kit/` into a target project.
- There is no required installer path.
- Worker/reviewer roles are model-agnostic.
- Evidence verdicts help review, but the reviewer/user owns final acceptance.
- Runtime state should stay inside `token-saver-kit/.ai/` in target projects.

## Development Setup

Requirements:

- Python 3.10+
- Git

Run tests:

```powershell
python -m unittest
```

Useful checks:

```powershell
git status --short
git diff --check
```

## Pull Request Guidelines

Before opening a pull request:

- Keep the change focused.
- Add or update tests when changing Python behavior.
- Update docs when changing the portable workflow.
- Avoid generated, binary, cache, build, and dependency folders.
- Do not introduce external dependencies unless the benefit is clear and discussed.

In the PR description, include:

- what changed
- why it matters
- validation commands and results
- any known risks or follow-up work

## Working On The Portable Kit

Be careful with files under `portable/token-saver-kit/` because users copy that folder directly into their projects. Prefer small, explicit changes and keep prompts compact so reviewer token usage stays low.

