# Implementation Options

## Chosen Direction: Portable-Only Kit

Token Saver Loop ships as a folder users copy into a project:

```text
token-saver-kit/
```

This keeps setup explicit, reversible, and easy to reason about. The kit owns its own state under:

```text
token-saver-kit/.ai/active_task/
```

## Rejected Direction: Installer Mode

Installer mode was removed for 1.0 because it added complexity without improving the main user experience:

- more paths to document
- more doctor branches
- more write safety logic
- more tests for a secondary setup path
- more risk of polluting target projects

## CLI Role

The Python CLI remains useful for read-only helpers:

- diagnostics with `--doctor`
- config preview
- worker skill preview
- token and metrics records

It should not write workflow kit files into target projects.
