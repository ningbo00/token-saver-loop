# Example: Bugfix Loop

This example shows a repeated debug loop where the worker absorbs noisy command
output and the reviewer stays focused on decisions.

## Task

A test is failing after a small refactor. The reviewer wants one bounded fix
attempt, not an open-ended rewrite.

Reviewer prompt:

```text
Read token-saver-kit/START_HERE.md and act as reviewer only.
Create a T1 worker round to diagnose and fix the failing test.
The worker may edit only the failing module and its test file.
Require the exact failing test command first, then the narrowest passing command.
Stop after one focused fix attempt if the cause is unclear.
```

## Worker Does

- Runs the failing command and records concise output in `tests.txt`.
- Reads only the failing code path.
- Applies one focused fix.
- Reruns the narrow validation.
- Reports whether the fix is implemented and validated.

Example acceptance shape:

```json
{
  "failing_test_fixed": {
    "implemented": true,
    "validated": true,
    "evidence": "test",
    "note": "narrow failing test now passes"
  }
}
```

## Reviewer Checks

- Did the worker stop after one focused attempt?
- Did it avoid unrelated refactors?
- Does the test evidence match the changed behavior?
- Is a broader regression test needed before pass?

## Token-Saving Point

The worker can spend tokens on noisy stack traces, retries, and local inspection.
The reviewer reads only the command summary, changed files, and the risk note.

