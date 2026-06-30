# Example: Codex Worker Round

This example shows how to use Token Saver Loop when your worker is a coding
agent that can edit files and run commands.

## Task

Improve a small CLI feature without letting the worker roam through the whole
repository.

Reviewer prompt:

```text
Read token-saver-kit/START_HERE.md and act as reviewer only.
Create a T2 worker round to add one focused CLI option.
Limit the worker to src/token_saver_loop/cli.py, src/token_saver_loop/core.py,
and tests/test_cli.py. Require python -m unittest tests.test_cli.
```

## Worker Does

- Reads `token-saver-kit/LATEST_WORKER_PROMPT.md`.
- Changes only the allowed files.
- Runs the required test command.
- Writes:
  - `worker_report.json`
  - `worker_log.md`
  - `tests.txt`
  - `diffstat.txt`
  - `round_status.json`

## Reviewer Checks

The reviewer reads the compact evidence first:

```text
Review the latest worker evidence in token-saver-kit and decide the next step.
```

Then the reviewer spot-checks:

- whether the file limit was respected
- whether tests passed
- whether `acceptance.*.validated` is true for the important behavior
- whether risks or open questions require a same-tier fix

## Token-Saving Point

The expensive reviewer model does not need to perform the file search, edit
attempts, command retries, or progress narration. It reviews the final evidence
packet and only expands into diffs when needed.

