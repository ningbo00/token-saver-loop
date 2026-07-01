# Token Saver Loop 产品介绍

这份文档目标是让重度 AI 编程用户在 10-20 分钟内明白：

- 它解决什么痛点
- 为什么值得信任
- 如何安装
- 如何跑第一轮
- 什么场景最值得用

## 工具定位

标题：

```text
Token Saver Loop ：别再让最贵的 AI 模型反复读文件、跑命令、试错和写进度
```

一句话：

```text
这是一个给重度 AI 编程用户用的本地工作流：强 reviewer 模型负责规划和验收，低成本 worker 模型负责执行、测试和提交证据。
```

目标观众：

- 每天用 Codex、Claude Code、Cursor、DeepSeek、Kimi、GLM、Qwen 等工具写代码的人
- 经常遇到上下文爆炸、模型任务漂移、token/额度消耗过快的人
- 同时使用多个模型，想让不同模型分工的人
- 想把 AI 编程过程变成可复盘本地证据的人


## 8 分钟短版流程

| 时间 | 环节 |
|---|---|
| 0:00-1:00 | 痛点：贵模型在做便宜活 |
| 1:00-2:30 | reviewer / worker 分工 |
| 2:30-4:30 | 复制 kit + 固定 prompt |
| 4:30-6:30 | 看 worker_report 和 review verdict |
| 6:30-8:00 | 哪些场景最省 token + GitHub 地址 |

## 开场逐字稿

```text
大家好，我今天介绍一个小工具，叫 Token Saver Loop。

它不是另一个 AI 编程模型，也不是新的 agent 框架。

它解决的是一个更日常的问题：如果你是重度 AI 编程用户，你会发现最贵的模型经常没有在做最贵的事情。

它在读文件、扫日志、跑命令、解释失败、重试、写进度。

这些工作很消耗上下文，也很消耗 token 或额度，但它们本质上是执行工作，不是判断工作。

Token Saver Loop 的想法很简单：

让强模型做 reviewer，只负责规划、设边界、最终验收。
让低成本模型做 worker，只负责执行、测试、提交证据。

这样贵模型不再被执行过程污染上下文，便宜模型承担噪音，但最终通过权仍然在 reviewer 手里。
```

## 核心概念讲法

```text
传统 AI 编程经常是一个模型从头做到尾：

它读需求，搜文件，改代码，跑测试，失败后重试，最后还告诉你它成功了。

问题是，同一个模型既执行又自审，很容易出现三个问题：

第一，token 烧得快。
第二，上下文越来越脏。
第三，自改自审不可靠。

Token Saver Loop 把它拆成两个角色：

Reviewer：强模型，负责判断。
Worker：低成本模型，负责执行。

每一轮 worker 都必须留下本地证据，比如改了哪些文件、跑了哪些命令、哪些验证通过、哪些风险没确认。

Reviewer 不看 worker 的口头保证，而是看证据决定 pass、fix、downgrade 或 stop。
```

## 安装演示脚本

演示目标：证明没有安装器、没有服务、没有账号、没有 API key 配置。

画面准备：

- 打开一个示例项目目录
- 打开 GitHub 仓库页面
- 打开终端或文件管理器

讲稿：

```text
安装方式非常朴素：没有安装器。

你只需要把这个仓库里的 portable/token-saver-kit 复制到你的项目根目录。

复制后，目标项目里会多一个 token-saver-kit 文件夹。

所有工作流状态都存在这个文件夹内部的 .ai 目录里。

如果你以后不想用了，删掉 token-saver-kit 就可以。
```

Windows CMD 命令：

```cmd
rmdir /S /Q "%TEMP%\token-saver-loop-kit" 2>NUL & git clone --depth 1 --branch v1.08 https://github.com/ningbo00/token-saver-loop.git "%TEMP%\token-saver-loop-kit" && xcopy "%TEMP%\token-saver-loop-kit\portable\token-saver-kit" "token-saver-kit" /E /I /Y && rmdir /S /Q "%TEMP%\token-saver-loop-kit"
```

安装后检查：

```text
目标项目/
  token-saver-kit/
    START_HERE.md
    LATEST_WORKER_PROMPT.md
    REVIEWER_CONTINUE.md
    tools/
    skills/
    .ai/
```

## 第一轮使用演示

### Step 1：Reviewer 启动

对 reviewer 模型发送：

```text
Read token-saver-kit/START_HERE.md and act as reviewer only.
Create a T0 inspect-only first task.
The worker should summarize the project structure and must not modify source code.
```

讲解：

```text
注意这里 reviewer 只负责规划，不直接改项目代码。

它会把 worker 的下一轮任务写进本地文件，并刷新 LATEST_WORKER_PROMPT.md。
```

### Step 2：Worker 执行

对 worker 模型发送：

```text
Read token-saver-kit/LATEST_WORKER_PROMPT.md and execute it.
```

讲解：

```text
worker 不需要知道上一段聊天历史。

它只读当前 handoff 文件，执行这一轮任务，然后把结果写回 token-saver-kit/.ai/active_task/rounds/。
```

### Step 3：看证据包

展示这些文件：

```text
token-saver-kit/.ai/active_task/rounds/round_001/
  round_status.json
  worker_report.json
  worker_log.md
  tests.txt
  diffstat.txt
```

讲解：

```text
这里最重要的不是 worker 说了什么，而是它留下了什么证据。

worker_report.json 里会有：
status、files_read、files_changed、commands_run、acceptance、risks、deviations、next_action。

如果有某个功能只是实现了但没有验证，它应该写 validated: false，而不是假装通过。
```

### Step 4：Reviewer 验收

对 reviewer 模型发送：

```text
Review the latest worker evidence in token-saver-kit and decide the next step.
```

讲解：

```text
reviewer 根据证据做决定：

PASS：接受，进入下一轮。
FIX_SAME_TIER：同权限修复。
DOWNGRADE：降低权限，收窄范围。
STOP：停止自动推进，让人来判断。

这就是 loop：reviewer 决策，worker 执行，worker 留证据，reviewer 再决策。
```

## 功能亮点讲解

### 1. Stable Prompt Path

```text
用户永远只需要给 worker 这一句：
Read token-saver-kit/LATEST_WORKER_PROMPT.md and execute it.

不需要手动找 round_001、round_002。
```

### 2. Evidence First

```text
Token Saver Loop 不信任模型自夸。

它要求 worker 写本地证据：改动文件、命令结果、风险、验证状态。
```

### 3. round_status.json

```text
round_status.json 用来避免 reviewer 读到半写完的报告。

worker 开始时是 in_progress，结束时才是 done。
```

### 4. Project Memory

```text
项目记忆在 token-saver-kit/.ai/project_memory/。

它不是无限聊天历史，而是紧凑的当前目标、风险、已接受工作和最新证据。
```

### 5. Red Flags

```text
工具可以检查常见问题：
缺少报告、验证失败、改动超范围、生成文件污染、危险 git 命令。

这些工具只给 evidence verdict，不替代 reviewer 最终验收。
```

## 适合和不适合

适合：

- 重度 AI 编程用户
- 经常多个模型配合使用的人
- 大仓库探索
- 循环 debug
- 批量改名、文档、i18n
- 想把 AI 执行过程保留成本地证据的人

不适合：

- 一句话问答
- 单文件极小修改
- 不在乎 token 或上下文成本的任务
- 希望 AI 完全自动决定并提交的人

讲法：

```text
这个工具不是让所有任务都变复杂。

如果任务 30 秒能做完，就直接做。

Token Saver Loop 适合的是那些执行过程很吵、但最终判断可以压缩成证据包的任务。
```

## 结尾 CTA

```text
如果你也是重度 AI 编程用户，经常觉得贵模型被文件读取、日志、重试和上下文污染拖住，可以试一下 Token Saver Loop。

GitHub 地址在视频简介里。

你可以先从 T0 inspect-only 任务开始，不改任何业务代码，只验证这个流程适不适合你。

如果这个思路对你有帮助，欢迎 star、提 issue，或者分享你的 reviewer/worker 模型组合。
```



## 直播/视频备注

- 开场不要先讲“portable kit”，先讲贵模型做便宜活。
- 安装演示一定要强调删除也简单：删 `token-saver-kit/`。
- 演示第一轮建议用 T0，安全且可信。
- 不要承诺所有任务都省 75%；说“执行噪音越多，收益越明显”。
- 不要把 worker 描述成低质量模型；描述成“执行模型”。
- 强调最终验收权在人/reviewer，不在 worker。
