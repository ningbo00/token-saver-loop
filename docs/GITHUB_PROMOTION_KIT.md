# GitHub Promotion Kit

Use this file when sharing Token Saver Loop in GitHub, forums, newsletters, or social posts.

## One-Line Pitch

Token Saver Loop is a portable workflow kit that keeps expensive reviewer models focused on judgment while cheaper worker models handle bounded execution and evidence collection.

## Short Description

Token Saver Loop helps AI coding users reduce premium-model context waste. Copy `portable/token-saver-kit/` into any project, let a strong reviewer model create bounded worker tasks, then let any compatible worker model execute, test, and write compact evidence for review.

## GitHub About Text

Portable reviewer/worker workflow kit for AI coding agents. Reduce premium model context waste by moving execution, retries, and evidence collection to bounded worker rounds.

## Suggested Topics

```text
codex
ai-coding
ai-agents
coding-agent
coding-agents
agent-workflow
ai-workflow
llm-workflow
context-management
token-optimization
developer-tools
claude-code
cursor
deepseek
kimi
glm
qwen
llm
llmops
prompt-engineering
```

## Launch Post

```text
I built Token Saver Loop, a portable workflow kit for AI coding agents.

The idea is simple:
- a strong reviewer model plans and accepts
- a cheaper worker model executes bounded rounds
- the worker writes compact evidence: files changed, commands, risks, validation
- the reviewer reads evidence instead of the entire execution chatter

No install path: copy portable/token-saver-kit/ into a repo and paste fixed prompts into your reviewer/worker models.

Best fit: repo exploration, repeated debug loops, bulk edits, docs/i18n drafts, and long tasks where context bloat gets expensive.

Repo: https://github.com/ningbo00/token-saver-loop
```

## Chinese Launch Post

```text
我做了一个给 AI 编程 agent 用的便携式工作流工具：Token Saver Loop。

核心思路：
- 高阶 reviewer 模型只负责规划和验收
- 低成本 worker 模型负责执行、测试、收集证据
- worker 每轮输出紧凑报告：改了哪些文件、跑了什么命令、风险在哪里
- reviewer 不再反复阅读完整执行过程，从而减少上下文和 premium token 浪费

不用安装：把 portable/token-saver-kit/ 复制到任意项目，然后按固定 prompt 启动 reviewer/worker。

适合：代码库探索、反复 debug、批量修改、文档/i18n、长任务上下文膨胀明显的场景。

GitHub: https://github.com/ningbo00/token-saver-loop
```

## Release Notes Draft

```text
Token Saver Loop 1.08

Highlights:
- Portable no-install workflow kit
- Reviewer/worker split for AI coding agents
- Stable LATEST_WORKER_PROMPT.md handoff path
- Round evidence files: worker_report.json, tests.txt, diffstat.txt
- round_status.json lifecycle marker to avoid reviewing half-written reports
- Evidence-shaped acceptance fields that separate implemented vs validated
- Setup doctor, red-flag checks, review summaries, token metrics helpers
- Beginner guide and minimal inspect-only starter task

Use the tagged kit:
rmdir /S /Q "%TEMP%\token-saver-loop-kit" 2>NUL & git clone --depth 1 --branch v1.08 https://github.com/ningbo00/token-saver-loop.git "%TEMP%\token-saver-loop-kit" && xcopy "%TEMP%\token-saver-loop-kit\portable\token-saver-kit" "token-saver-kit" /E /I /Y && rmdir /S /Q "%TEMP%\token-saver-loop-kit"
```
