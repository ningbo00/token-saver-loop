# Product Brief — Token Saver Loop

## 1. 项目名理解
**Token Saver Loop** 在这里被重新定位为 **"Get Project To Whatever workflow"**：把一个可复用的 Kimi-Codex 半自动协作工作流，安装到任意代码项目中。
核心隐喻是 **"Drop-in workflow kit"** —— 让任何项目都能低成本获得 "Codex 规划/审阅 + Kimi 低耗执行" 的协作模式。

## 2. 要解决的问题
- 开发者想在自己的多个项目中使用 Kimi-Codex 协作模式，但每次都需手动复制工作流脚本、目录结构和规范文件。
- 没有轻量、统一的方式把 Kimi-Codex 工作流"安装"进一个新仓库。
- 不同项目的 Codex 审阅标准和 Kimi 执行规则需要 project-local 的 skill 文件，但手工维护容易遗漏。

## 3. 推荐 MVP 目标
一个**本地 Python CLI 工具**，能够：
1. 接收一个目标项目名称和可选配置（如测试命令）。
2. 生成并预览一套标准的 Kimi-Codex 工作流文件（目录结构、状态文件、工具脚本、skill 文件）。
3. 未来版本支持将这些文件实际写入目标目录（本轮只读/预览，不做真实安装）。
4. 安装后的项目即可获得：`.ai/active_task/` 状态管理、`docs/` 项目文档、`tools/` 工作流脚本、`.kimi-code/skills/` 本地 worker skill。

MVP 不做：真实文件写入安装器、远程同步、多项目并行管理、GUI。

## 4. 非目标
- 不是 LLM 输出转换器（旧方向已 pivot）。
- 不做 SaaS、不做多租户、不做数据库持久化。
- 不做通用的 AI Agent 编排框架。
- 本轮不做真实的文件系统安装操作。

## 5. 第一版用户流程（MVP）
```
用户打开终端
    |
    v
运行 Token Saver Loop，指定项目名和可选测试命令
    |
    v
预览生成的项目配置、skill 文件内容、计划安装路径
    |
    v
用户确认后，在后续版本中执行真实安装
```

示例命令（示意）：
```bash
# 预览项目配置
token-saver-loop --project-name MyApp --test-command "pytest" --show-config

# 预览生成的 worker skill
token-saver-loop --project-name MyApp --test-command "npm test" --show-project-skill

# 列出计划安装路径
token-saver-loop --list-install-paths
```

## 6. 需要用户 / Codex 决策的问题

| 问题 | 选项/说明 |
|---|---|
| **真实安装行为** | 本轮只做预览/打印；下一轮是否加入 `--install` 标志执行真实文件写入？ |
| **PowerShell 脚本来源** | 是否将 tools/ 下的 .ps1 脚本作为内嵌模板打包进 Python 包，还是保留为外部文件引用？ |
| **Skill 文件模板** | 当前 render_project_worker_skill 生成静态文本；未来是否需要 Jinja2 等模板引擎？ |
| **配置持久化** | default_project_config 返回内存 dict；未来是否写入 `token-saver-loop.toml` 或 `.ai/config.json`？ |


