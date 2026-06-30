# Security Policy

Token Saver Loop is a portable workflow kit for AI-assisted development. It does not require a server, account, API key, or background service.

## Supported Versions

Security reports should target the latest code on `master` or the latest GitHub release.

## Reporting A Vulnerability

Please report security concerns privately when public disclosure could put users at risk. Contact the repository owner through the GitHub profile associated with this repository.

When reporting, include:

- affected file or workflow
- steps to reproduce
- expected impact
- whether the issue affects the portable kit, helper CLI, docs, or generated task state
- any suggested fix

Do not include secrets, private repository content, or sensitive logs in public issues.

## Security Boundaries

Important defaults:

- The kit is local-file based and does not phone home.
- Worker prompts forbid destructive git operations by default.
- Worker prompts forbid generated, binary, dependency, build, and cache areas unless explicitly allowed.
- Review tools produce evidence verdicts only; they do not replace human/reviewer acceptance.

## Not Security Boundaries

Token Saver Loop cannot guarantee that an AI model will always follow instructions. Users should still inspect diffs, run tests, and avoid giving workers unnecessary permissions.

