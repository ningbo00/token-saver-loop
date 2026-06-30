# AGENT_CONTEXT

Project: Token Saver Loop

Status:
- Token Saver Loop is the primary product path; worker/reviewer are generic roles, and specific model names are examples only.
- README is GitHub-facing; `docs/BEGINNER_GUIDE.md` is the beginner path for users new to the workflow.
- Package version is `1.0.6`; JSON schemas remain `version: 1`.
- CLI supports project config preview, worker skill preview, setup doctor reports, worker token usage parsing, manual reviewer usage snapshots, metrics summarization, and metrics append/write.
- There is no installer mode; the product path is copying `portable/token-saver-kit/`.
- First-run portable workflow has been hardened: reviewer/worker prompts are short, detailed role rules live in kit skills, and tools are optional low-friction bookkeeping helpers.
- Evidence verdicts are conservative tool outputs (`PASS`, `FIX_SAME_TIER`, `DOWNGRADE`, `STOP`) and never replace reviewer acceptance.
- Project memory lives in kit-local `.ai/project_memory/`; keep it compact and read only the needed files.
- Reviewer plans/reviews; any compatible worker model executes bounded rounds from `token-saver-kit/LATEST_WORKER_PROMPT.md`.
- GitHub packaging pass added root MIT LICENSE, a minimal example, and portable kit-local `.gitignore`; root `.ai/` and `.token-saver/` should stay local-only.

Current Goal:
- Finalize portable kit and GitHub-first README for a commit-ready 1.0 workflow kit.
- Keep portable/no-install usage as the only workflow setup path.
- Next optimization candidates: add a small first-run fixture test around portable `round_NNN` generation, then prepare release packaging.
- After creating the GitHub repo, optionally add real `project.urls` metadata to `pyproject.toml`.

Rules:
- Keep tasks small.
- Apply Token Saver Loop to this repo's own work by routing on cost shape, not habit: use a low-cost worker when execution/search/bulk generation is large and reviewer work can stay compact.
- Do not delegate when the reviewer would need to fully reread and rewrite the result anyway; judgment-heavy or short high-concept work should stay with the reviewer.
- For worker batches, require a review pack that makes reviewer review smaller than direct execution: files changed, key decisions, uncertain points, high-risk sections, and validation.
- Split by risk and review cost: high-risk code/security changes stay small; low-risk docs/i18n/bulk text can be one bounded batch only if the review pack is compact.
- Trust diff, files, and tests over model claims.
- The worker must write round logs under `.ai/active_task/rounds/`.
- Batch size is dynamic: increase after clean worker passes, reduce after failures or drift.
- Larger batches must still be executed as multiple small checkpointed steps, not one large leap.
- Reviewer thread rotation: suggest a fresh reviewer thread after commits, phase boundaries, release decisions, or 2-3 clean worker passes; not after every same-tier fix.
- Worker process rotation: prefer a fresh worker conversation per round when handoff files are current; the worker should follow repo handoff, not chat memory.
- Fresh reviewer threads can start by reading root `REVIEWER_CONTINUE.md`.
- The worker should update `.ai/active_task/progress.md` at the end of each round as a user-facing rough progress board; reviewer may use it for navigation only, not verification.




