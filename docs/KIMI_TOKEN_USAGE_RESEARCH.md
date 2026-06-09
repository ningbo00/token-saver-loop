# Kimi Token Usage Research

> Round 004 — T0 research-only task.
> Goal: determine whether KimiCode VS Code plugin exposes real token usage data.

## Summary

**Real token usage data exists in local session files, but the VS Code UI does not surface it.**
The underlying Kimi CLI records a running `token_count` in `context.jsonl`. A project script can read this file automatically, but only total tokens are available—there is no prompt/completion breakdown.

---

## 1. Does KimiCode VS Code show token usage in the UI?

**No.**

Evidence inspected:
- `package.json` (VS Code extension manifest): no configuration property for token display, no command to show usage.
- `readme.md`: does not mention token usage, cost, or billing metrics.
- `webview-ui/`: no compiled UI strings referencing token or usage counts.
- Command palette commands (`kimi.showLogs`, `kimi.newConversation`, etc.): none related to usage display.

Conclusion: the plugin does not expose token usage through the VS Code chat UI, sidebar, or command palette.

---

## 2. Does it expose token usage in output panels, logs, or local traces?

**Partially — in local session files, not in the UI output panel.**

Evidence inspected:
- `~/.kimi/logs/kimi.log`: no `token` or `usage` lines found.
- `~/.kimi/sessions/<hash>/<uuid>/context.jsonl`: **contains `_usage` entries**.

Sample entry:
```json
{"role": "_usage", "token_count": 13105}
```

Across the current active session there are **110 `_usage` entries** ranging from ~13k to ~96k tokens.

The VS Code output panel (accessible via `kimi.showLogs`) appears to show the CLI process log, which does **not** include these `_usage` records. They are stored silently in the session context file.

---

## 3. Does it have a config option to enable debug logs or usage metadata?

**No dedicated token-logging config.**

Evidence inspected:
- `~/.kimi/config.toml`: no `token`, `usage`, `log_usage`, or similar key.
- CLI `--help`: offers `--debug` and `--verbose`, but no usage-specific flag.
- Extension `package.json` settings (`kimi.yoloMode`, `kimi.autosave`, `kimi.showThinkingContent`, etc.): none related to usage logging.

Conclusion: token metadata is already written to `context.jsonl` without requiring a config toggle.

---

## 4. Does the underlying API response include usage fields?

**Yes, inferred from the `_usage` records.**

The Kimi/Moonshot API (like OpenAI-compatible APIs) normally returns a `usage` object containing:
```json
{
  "usage": {
    "prompt_tokens": 1200,
    "completion_tokens": 800,
    "total_tokens": 2000
  }
}
```

However, Kimi CLI appears to **consume only the total** and discard the prompt/completion breakdown. The `_usage` entries contain only:
```json
{"role": "_usage", "token_count": <total>}
```

There is **no prompt_tokens or completion_tokens** in the local trace.

---

## 5. Can a project script read these usage values automatically?

**Yes, with caveats.**

A script can:
1. Locate the active session directory under `~/.kimi/sessions/`.
2. Find the correct sub-directory (UUID).
3. Parse `context.jsonl` and filter lines where `role == "_usage"`.
4. Extract `token_count`.

Caveats:
- Session directories are hashed (`<session_hash>/<uuid>/`). Mapping a project workspace to its session requires reading `~/.kimi/kimi.json` (work_dirs list) or matching by timestamp.
- The file is append-only JSONL; a script can tail it or read it at round boundaries.
- **No prompt/completion split** means cost attribution is approximate.

---

## 6. Best fallback if automatic reading fails

| Fallback | Pros | Cons |
|---|---|---|
| **Semi-automatic `context.jsonl` reader** | Accurate total tokens; no user input needed | Requires knowing session UUID; no split |
| **Tiktoken / token estimator** | Works offline; gives prompt/completion split | Requires dependency install; model-specific; only estimated |
| **Manual entry** | Simple; works everywhere | Error-prone; friction per round |

**Recommendation:**
1. **Primary**: implement a small helper that reads the latest `_usage` line from `~/.kimi/sessions/*/context.jsonl` (filtered by project path from `kimi.json`).
2. **Fallback**: if the file is inaccessible, record `"source": "unavailable"` and let the user paste a number manually.
3. Do **not** add tiktoken as a dependency until the workflow requires cost-split accuracy.

---

## 7. Proposed `token_usage.json` schema

```json
{
  "version": 1,
  "project_name": "Token Saver Loop",
  "entries": [
    {
      "round": "004",
      "tier": "T0",
      "timestamp": "2026-06-09T00:30:00+08:00",
      "session_id": "575ae8a66c8d97f7907f260216fb108e",
      "token_count": 94975,
      "estimated_prompt_tokens": null,
      "estimated_completion_tokens": null,
      "source": "kimi_context_jsonl",
      "notes": "Total only; no prompt/completion split from CLI"
    }
  ],
  "summary": {
    "total_rounds": 4,
    "last_token_count": 94975,
    "peak_token_count": 94975
  }
}
```

Reserved fields for future actual usage:
- `prompt_tokens` — if Kimi CLI ever exposes the split.
- `completion_tokens` — same.
- `model` — the model name used (e.g., `kimi-latest`).
- `cost_usd` — estimated cost if a price table is added later.

---

## 8. What Kimi should record in each round log when exact usage is unavailable

In `.ai/active_task/rounds/round_XXX/kimi_log.md`, add a new section:

```markdown
## Token Usage
- Source: kimi_context_jsonl | estimate | manual | unavailable
- Total tokens: <number> or "N/A"
- Prompt tokens: <number> or "not provided by CLI"
- Completion tokens: <number> or "not provided by CLI"
- Peak context: <max token_count seen in session>
```

If automatic reading fails, record:
```markdown
## Token Usage
- Source: unavailable
- Reason: ~/.kimi/sessions context.jsonl not readable or session not yet flushed
- Action: user may paste usage from Kimi web dashboard if needed
```

---

## Research boundaries observed

- Did **not** read `~/.kimi/credentials/` (sensitive).
- Did **not** read API keys or auth tokens.
- Did **not** access the network.
- Did **not** modify source code.
- Inspected only non-sensitive metadata: extension manifest, README, CLI help, public config files, and session context traces.

