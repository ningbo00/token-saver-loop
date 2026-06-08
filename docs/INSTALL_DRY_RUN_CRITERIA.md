# Acceptance Criteria: `--install --dry-run`

> Status: Implemented (dry-run MVP). Real installation writes are still not implemented.

## Overview

A future `--install --dry-run` flag should simulate what the installer would write without touching the file system. This lets users preview the effect of `gpt2whatever --install` before committing to it.

## Functional Criteria

1. **Command exists and is recognized**
   - `gpt2whatever --install --dry-run` parses successfully.
   - `gpt2whatever --install` without `--dry-run` prints a clear message that real installation is not yet implemented.

2. **Dry-run produces a deterministic preview**
   - The CLI prints a JSON or structured text listing every file that would be created or modified.
   - Each entry includes: `path`, `action` (`create` or `modify`), and a short `reason`.

3. **Preview matches planned install paths**
   - The listed paths must match `planned_install_paths()` in `core.py`.
   - If `--project-name` is provided, project-specific paths (e.g., `.kimi-code/skills/<project>-kimi-codex-worker/SKILL.md`) are included.

4. **No file system mutations**
   - Running `--install --dry-run` must not create directories, write files, or modify `state.md`.
   - A safety check in tests verifies no disk writes occurred.

5. **Conflict detection (preview-only)**
   - If a target path already exists, the dry-run output marks it as `conflict: existing`.
   - The CLI exits with code 0 (preview succeeded) but the output clearly flags conflicts.

6. **Respects `--project-name` and `--test-command`**
   - When `--project-name` is omitted, the dry-run uses a placeholder or errors clearly.
   - When `--test-command` is provided, it appears in the generated skill preview.

7. **Project name validation**
   - `--project-name` must contain only letters, digits, underscores, and hyphens.
   - Names with path separators, traversal sequences (`..`), or whitespace are rejected with a clear error.

## Non-Functional Criteria

7. **Output format stability**
   - The dry-run output schema is versioned (e.g., `{"version": 1, "actions": [...]}`).
   - Tests assert the schema shape so future changes are explicit.

8. **Performance**
   - Dry-run completes in under 1 second for a default project config.

## Test Coverage (future)

- CLI returns 0 for `--install --dry-run --project-name MyApp`.
- CLI returns non-zero for `--install` without `--dry-run`.
- Output JSON contains expected paths from `planned_install_paths()`.
- Existing files are flagged as conflicts in the preview.
- No files are created on disk during dry-run tests.

## Out of Scope (for dry-run)

- Real file-system writes.
- Overwrite prompts or backup logic.
- Post-install verification (e.g., running tests after install).
