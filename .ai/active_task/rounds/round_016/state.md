# Round 016 — Preflighted Bulk Install Helper

## Goal
Add `apply_install_plan(actions, target_root)` in `core.py` with all-or-nothing semantics: validate every action before writing any files. Only `create` actions are allowed. No partial writes on conflict or outside-root errors.

## Changes
- **`src/gpt2whatever/core.py`**: Added `apply_install_plan(actions, target_root)`.
  - Rejects non-list `actions`.
  - Iterates all actions once for validation: every action must have `path`, `action == "create"`, and an explicit `"content"` key.
  - Then calls `apply_install_action` for each action; any exception aborts all writes.
- **`tests/test_core.py`**: Added `TestApplyInstallPlan` with 6 tests:
  - `test_creates_multiple_files`
  - `test_conflict_aborts_all`
  - `test_traversal_aborts_all`
  - `test_missing_content_aborts_all`
  - `test_non_create_action_aborts_all`
  - `test_empty_content_allowed`

## Tests
137 tests passed. See `tests.txt`.

## Artifacts
- `state.md`
- `tests.txt`

## Decisions
- Used explicit `"content"` key requirement instead of `get("content", "")`, to force callers to be intentional. Empty string content is still allowed.
- All-or-nothing is implemented by relying on `apply_install_action` raising on first error; since all writes happen sequentially, the abort guarantees no partial writes for `create` actions (none are destructive).

## Next
Wire `apply_install_plan` into CLI `--install` real-write path (still behind a flag or confirmation gate).
