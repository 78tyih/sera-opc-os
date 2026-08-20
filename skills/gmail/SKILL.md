---
name: gmail
purpose: 通过 Gmail API（托管 OAuth，经 Maton 代理）读取、发送、管理邮件、线程、标签和草稿。
inputs: Gmail 操作意图（读/发/管理邮件、线程、标签、草稿）；MATON_API_KEY；Gmail 账户 OAuth 连接。
outputs: 邮件列表/正文、发送结果、线程/标签/草稿管理结果（JSON）。
workflow: |
  1. 前置：maton whoami 确认登录；maton connection list google-mail --status ACTIVE 确认 Gmail 连接
  2. CLI：maton google-mail message list -L 10（快捷子命令）
  3. 或通用：maton api '/google-mail/gmail/v1/users/me/messages?maxResults=10'（原生 API 路径）
  4. Python 直调：urllib + Authorization Bearer MATON_API_KEY 访问 https://api.maton.ai/google-mail/{native-api-path}
tools: Bash（maton CLI）, Python（urllib 直调可选）
examples: |
  - maton google-mail message list -L 10
  - maton api '/google-mail/gmail/v1/users/me/messages?maxResults=10'
  - maton login（浏览器获取 API key）/ maton login --interactive
iron_rules: |
  - 需要有效 MATON_API_KEY 与网络；OAuth 连接管理在 https://api.maton.ai
  - 第三方应用不在本 skill（用 api-gateway skill）
source: ~/.workbuddy/skills/gmail/SKILL.md
---

# gmail

## Purpose
通过 Gmail API（托管 OAuth 认证，经 Maton 代理 `api.maton.ai`）读取、发送、管理 Gmail 邮件、线程、标签和草稿。Maton 代理自动注入 OAuth token。

## Inputs
- Gmail 操作意图（读 / 发 / 管理邮件、线程、标签、草稿）
- `MATON_API_KEY`（环境变量）；Gmail Google OAuth 连接（在 api.maton.ai 管理）

## Outputs
- 邮件列表 / 正文、发送回执、线程 / 标签 / 草稿管理结果（JSON）

## Workflow
```
1. 前置：maton whoami（登录态）→ maton connection list google-mail --status ACTIVE（Gmail 连接）
2. CLI 快捷子命令：maton google-mail message list -L 10
3. 通用原生 API：maton api '/google-mail/gmail/v1/users/me/messages?maxResults=10'
4. Python 直调（可选）：urllib + Bearer {MATON_API_KEY} → https://api.maton.ai/google-mail/{native-api-path}
```

## Tools
- Bash：`maton` CLI（`maton google-mail ...` 子命令 / `maton api ...` 原生路径 / `maton login` / `maton whoami` / `maton connection list`)
- Python（可选）：urllib 直调 API

## Examples
```bash
# 安装
npm install -g @maton-ai/cli        # 或 brew install maton-ai/cli/maton

# 认证
maton login                          # 浏览器获取 API key
maton login --interactive            # 粘贴 API key
maton whoami                         # 查看认证状态

# 查连接
maton connection list google-mail --status ACTIVE

# 读邮件
maton google-mail message list -L 10
maton api '/google-mail/gmail/v1/users/me/messages?maxResults=10'
```

## Iron Rules
- 需要有效 `MATON_API_KEY` 与网络访问；OAuth 连接状态在 `https://api.maton.ai` 管理
- 第三方应用（非 Gmail）不在本 skill 范围（走 api-gateway）

## Source
`~/.workbuddy/skills/gmail/SKILL.md`
