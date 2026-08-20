---
name: context-hub
purpose: 读取并维护 Sera Context Hub（~/SeraContextHub/）——Trae/WorkBuddy/Codex/ChatGPT 共用的跨 Agent 规范上下文仓库，遵守 AGENT_CONTEXT_PROTOCOL 的 SESSION START/END。
inputs: 涉及 Sera-Factory / PropFirm-TV / Digital-Human / Sera-Workspace 任一项目的任务；多 Agent 交接/状态同步需求。
outputs: 会话开始时读取的全局+项目上下文；会话结束时更新的 CURRENT_STATE.md / AGENT_HANDOFF.md / TASKS.md / ASSET_INDEX.md / ADR；追加的 MEMORY.jsonl；02_Sessions 会议纪要；本地 git 提交。
workflow: |
  SESSION START（每次会话开始）：
  1. 读 00_Global/GLOBAL_CONTEXT.md + USER_PREFERENCES.md
  2. 读目标项目 01_Projects/<项目>/：CONTEXT.md → CURRENT_STATE.md → TASKS.md → AGENT_HANDOFF.md
  3. 涉资产 → ASSET_INDEX.md；涉历史 → MEMORY.jsonl 尾部 20 行
  4. 关联既有工作区 → 先读该工作区 .workbuddy/memory/ 最近日志

  SESSION END（收尾必做）：
  1. 覆写项目 CURRENT_STATE.md
  2. 更新 AGENT_HANDOFF.md（结论/遗留/BLOCKED）
  3. 追加 MEMORY.jsonl（id M-YYYYMMDD-<NNNN> 续号，type: decision/lesson/fact/preference/handoff/milestone/correction，只写已验证）
  4. 更新 TASKS.md / ASSET_INDEX.md；重大决策 → 03_Decisions/ADR
  5. 02_Sessions/YYYY-MM-DD-<短题>.md 补记
  6. cd ~/SeraContextHub && git add -A && git commit -m "YYYY-MM-DD workbuddy: <摘要>"
tools: Read, Bash（git add/commit）, Edit, Write
examples: |
  - "更新一下 Sera-Factory 的交接文档" → SESSION END 流程 1-6
  - "我上次在 PropFirm-TV 项目做到哪了" → SESSION START 流程 1-4
  - "记录这个决定" → 追加 MEMORY.jsonl（decision 类型）+ ADR
iron_rules: |
  - MEMORY.jsonl 只追加永不覆写；纠错追加 correction 条目
  - 凭证不写 Hub；本仓库纯本地不推远端
  - 双写原则：工作区 .workbuddy/memory/ 照常写；Hub 只收跨项目长期内容
  - 纯闲聊/一次性查询不强制读写
source: ~/.workbuddy/skills/context-hub/SKILL.md
---

# context-hub

## Purpose
读取并维护 Sera Context Hub（`~/SeraContextHub/`）——Trae / WorkBuddy / Codex / ChatGPT 共用的跨 Agent 规范上下文仓库。遵守 `AGENT_CONTEXT_PROTOCOL` 的 SESSION START / SESSION END 协议，保证多 Agent 间上下文连续、状态可交接。

## Inputs
- 涉及 Sera-Factory / PropFirm-TV / Digital-Human / Sera-Workspace 任一项目的实质性工作
- 需要跨 Agent 同步、交接状态、查询历史决策的任务

## Outputs
- SESSION START：读取的全局上下文 + 项目上下文（CONTEXT / CURRENT_STATE / TASKS / AGENT_HANDOFF）
- SESSION END：更新的 CURRENT_STATE.md / AGENT_HANDOFF.md / TASKS.md / ASSET_INDEX.md / ADR
- 追加的 MEMORY.jsonl、02_Sessions 纪要、本地 git commit

## Workflow
```
SESSION START
  1. 读 00_Global/GLOBAL_CONTEXT.md + USER_PREFERENCES.md
  2. 读 01_Projects/<项目>/：CONTEXT.md → CURRENT_STATE.md → TASKS.md → AGENT_HANDOFF.md
  3. 涉资产 → ASSET_INDEX.md；涉历史 → MEMORY.jsonl 尾部 20 行
  4. 关联既有工作区 → 读该工作区 .workbuddy/memory/ 最近日志

SESSION END（收尾必做）
  1. 覆写项目 CURRENT_STATE.md
  2. 更新 AGENT_HANDOFF.md（结论/遗留/BLOCKED）
  3. 追加 MEMORY.jsonl（id M-YYYYMMDD-<NNNN> 续号）
  4. 更新 TASKS.md / ASSET_INDEX.md；重大决策 → 03_Decisions/ADR
  5. 02_Sessions/YYYY-MM-DD-<短题>.md 补记
  6. cd ~/SeraContextHub && git add -A && git commit -m "YYYY-MM-DD workbuddy: <摘要>"
```

## Tools
- Read（读协议文件与项目上下文）
- Bash（`cd ~/SeraContextHub && git add -A && git commit`）
- Edit / Write（更新状态与记忆文件）

## Examples
- 「更新一下 Sera-Factory 的交接文档」→ SESSION END 流程 1-6
- 「我上次在 PropFirm-TV 项目做到哪了」→ SESSION START 流程 1-4
- 「记录这个决定」→ 追加 MEMORY.jsonl（decision 类型）+ ADR

## Iron Rules
- MEMORY.jsonl **只追加永不覆写**；纠错追加 `correction` 条目
- 凭证不写 Hub；本仓库纯本地、不推远端
- 双写原则：工作区 `.workbuddy/memory/` 照常写；Hub 只收跨项目长期内容，避免重复
- 纯闲聊 / 一次性查询不强制读写

## Source
`~/.workbuddy/skills/context-hub/SKILL.md`
