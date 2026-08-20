---
name: lark-unified
purpose: 统一飞书/Lark CLI 套件（lark-cli）：200+ 命令覆盖 18 个业务域（im/docs/drive/sheets/base/calendar/task/mail/wiki/contact/slides/markdown/vc/minutes/okr/approval/attendance/apps）。三层命令模型（shortcuts / API 命令 / raw API）+ 非 TTY 设置路径；飞书项目（Meegle）工作项按需转子技能。
inputs: 飞书/Lark 操作意图（发消息/搜聊天/建文档/查 Base/管日程/读邮件/办审批/调任意 OpenAPI）；lark-cli 已授权凭据；chat_id/app_token/spreadsheet_token 等实体 ID。
outputs: 对应业务域执行结果（消息回执/文档内容/Base 记录/日程/邮件/审批实例/OpenAPI 原始响应），JSON 信封 {ok, identity, data}。
workflow: |
  0. 产品路由：先判断是 Lark 协作还是飞书项目(Meegle)——信号词优先；歧义则问用户
  1. Preflight：python3 lark_status.py --json 检查 lark-cli 是否安装/配置/登录
  2. 授权：按需最小 scope（--scope "base:record:read ..."）；split-flow（--print-url-only 结束回合 → --device-code）
  3. 命令：Tier1 shortcuts（im +messages-send）→ Tier2 API 命令（calendar calendars list）→ Tier3 raw API（api GET /open-apis/...）
  4. 校验 JSON 契约：看 ok==true 或退出码，绝不用 code==0；高险写无 --yes 退出码 10 → 用户确认后重跑
  5. 相对路径：--file/--output 拒绝绝对路径
tools: Bash（lark-cli、python3 脚本）, Read（references/ 域参考按需）
examples: |
  - lark-cli im +chat-search --keyword "engineering"
  - lark-cli im +messages-send --chat-id oc_xxx --text "Hello team" --as bot
  - lark-cli calendar +agenda --as user
  - lark-cli docs +create --doc-format markdown --content $'<title>Weekly</title>\n  # Progress'
  - lark-cli sheets +csv-get --spreadsheet-token <token> --range 'Sheet1!A1:D20' --as user
  - lark-cli base +record-list --app-token <app_token> --table-id tbl_xxx --page-all
iron_rules: |
  - 产品路由优先：Meegle 信号（飞书项目/工作项/需求单/迭代/节点流转/MQL/project.feishu.cn URL）→ 转子技能；切勿用 lark-cli task/approval 顶替 Meegle 需求
  - 最小权限授权：默认 --scope 精确授权；--domain base=40 scope 而读表只需 3 个；--domain all 是最后手段
  - JSON 契约：检查 ok==true 或退出码；无顶层 code；错误信封看 error.type/missing_scopes
  - 退出码 10 = 审批门禁，须用户确认后 --yes，绝不自动追加 --yes
  - --file/--output 只收相对路径；绝不打印 appSecret/access token
  - 从不 grep "app_id"（config show 输出是 camelCase appId）——用 lark_status.py
source: ~/.workbuddy/skills/lark-unified/SKILL.md
---

# lark-unified

## Purpose
统一飞书 / Lark CLI 套件（封装官方 `lark-cli`）：200+ 命令覆盖 18 个业务域（im / docs / drive / sheets / base / calendar / task / mail / wiki / contact / slides / markdown / vc / minutes / okr / approval / attendance / apps）。三层命令模型（shortcuts / API 命令 / raw API 2500+ 端点）+ 非 TTY 设置路径。飞书项目（Meegle）工作项需求路由到内置子技能。

## Inputs
- 飞书 / Lark 操作意图（发消息、搜聊天、建文档、查 Base、管日程会议、读邮件、管理任务 wiki、办审批、调任意 OpenAPI）
- lark-cli 已授权凭据（bot 或 user 身份）
- 实体 ID：`open_id`(ou_)、chat `oc_`、message `om_`、`app_token`+`tbl_`、`spreadsheet_token`、wiki `space_id`+`node_token`、`calendar_id`+`event_id`、`task_guid`

## Outputs
- 对应业务域执行结果；JSON 信封：成功 `{"ok":true,"identity":"user","data":{...}}`，错误 `{"ok":false,"error":{"type":...,"missing_scopes":[...]}}`
- 错误时含 `console_url` / `hint` 指引

## Workflow
```
0. 产品路由：Lark 协作 vs 飞书项目(Meegle)——信号词优先；歧义问用户，不"两个都试"
1. Preflight：python3 lark_status.py --json（安装/配置/登录状态，看退出码）
2. 授权：按需最小 scope（--scope）；split-flow（turn1 --print-url-only 结束回合 → turn2 --device-code）
3. 命令三层：Tier1 shortcuts → Tier2 API 命令 → Tier3 raw API（调用前 lark-cli schema 查看）
4. 校验：看 ok==true 或退出码；高险写退出码 10 → 用户确认后 --yes
5. 相对路径：--file/--output 拒绝绝对路径（可用 - 读 stdin）
```

## Tools
- Bash：`lark-cli`（auth/config/im/docs/drive/sheets/base/calendar/task/mail/wiki/contact/slides/markdown/vc/minutes/okr/approval/attendance/apps）、`lark_status.py` / `lark_setup.py`、`meegle`（按需）
- Read：`references/` 各域参考（含 Permissions 表）

## Examples
```bash
# 发送消息（先搜 chat）
lark-cli im +chat-search --keyword "engineering"
lark-cli im +messages-send --chat-id oc_xxx --text "Hello team" --as bot

# 今日日程（个人资源必须 --as user）
lark-cli calendar +agenda --as user

# 从 markdown 建文档
lark-cli docs +create --doc-format markdown --content $'<title>Weekly Report</title>\n  # Progress\n- Shipped X'

# 读表格区域（A1 引用要加引号，防 ! 触发 history expansion）
lark-cli sheets +csv-get --spreadsheet-token <token> --range 'Sheet1!A1:D20' --as user

# 查 Base 记录（分页）
lark-cli base +record-list --app-token <app_token> --table-id tbl_xxx --page-all --page-limit 5

# 预览高险写
lark-cli im +messages-send --chat-id oc_xxx --text "test" --dry-run
```

## Iron Rules
- **产品路由优先**：Meegle 信号（飞书项目/工作项/需求单/缺陷/迭代/排期/节点流转/MQL/project.feishu.cn 或 meegle.com URL）→ 加载子技能；切勿用 `lark-cli task`/`approval` 顶替 Meegle 需求
- **最小权限授权**：默认 `--scope` 精确授权；`--domain base` 请求 40 个 scope 而读一张表只需 3 个；`--recommend` 请求 310 个 scope（含 13 个 delete）；`--domain all` 是最后手段
- **JSON 契约**：检查 `ok == true` 或退出码；**无顶层 `code`**；错误看 `error.type` / `missing_scopes`。用 `{"code":0}` 判断成功会把每次成功误判为失败（写操作危险）
- **退出码 10 = 审批门禁**：展示待确认动作 → 用户确认 → 重新带 `--yes`；绝不自动追加 `--yes`
- **身份**：个人资源（日历/邮件/drive）必须 `--as user`；bot 缺 scope 时把 `console_url` 交给用户，不为 bot 跑 `auth login`
- `--file`/`--output`/`--output-dir` 只收**相对路径**；绝不打印 `appSecret` / access token
- 从不 grep `app_id`（输出是 camelCase `appId`）——用 `lark_status.py` 解析

## Source
`~/.workbuddy/skills/lark-unified/SKILL.md`
