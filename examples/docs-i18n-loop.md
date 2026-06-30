# Example: Docs And I18n Loop

This example shows a low-risk batch where the worker drafts repetitive text and
the reviewer checks consistency.

## Task

Update localized README files after the English README changes.

Reviewer prompt:

```text
Read token-saver-kit/START_HERE.md and act as reviewer only.
Create a T2 worker round to sync the Quick Start wording from README.md into
README.zh-CN.md, README.ja.md, and README.ko.md.
The worker must preserve existing structure and links.
Require a concise diffstat and note any terms it is uncertain about.
```

## Worker Does

- Reads the English source section and the corresponding localized sections.
- Updates only the allowed README files.
- Records changed sections and uncertain terminology.
- Avoids touching code or generated files.

## Reviewer Checks

- Are the instructions structurally equivalent across languages?
- Did links and command snippets stay intact?
- Are uncertain translations clearly flagged?
- Is a native-speaker pass needed before release?

## Token-Saving Point

The worker performs the repetitive drafting. The reviewer focuses on source
alignment, command correctness, and flagged terminology instead of reading every
sentence as if it were a fresh task.

