---
name: wecom-unified
purpose: 企业微信 CLI 全能套件（wecom-cli）：覆盖通讯录、文档、在线表格、智能表格、智能文档、日程、会议、待办、微盘、邮件、消息、媒体文件等业务域。按姓名/拼音/英文名/别名找人、读写文档表格、管理日程会议待办、发消息等。
inputs: 办公意图（找人/文档/表格/日程/会议/待办/微盘/邮件/发消息）；doc.weixin.qq.com / page.weixin.qq.com / drive.weixin.qq.com 链接；wecom-cli 已授权。
outputs: 可读名称形式的业务结果（联系人信息、文档内容、表格读写、日程/会议/待办数据、微盘文件、邮件、消息回执）；内部 ID 仅在内部流转。
workflow: |
  0. 前置检查：wecom-cli --version（≥1.1.0，否则 npm install -g @wecom/cli）→ wecom-cli auth show --status（authorized 才继续；否则 wecom-cli auth init 扫码）
  1. 路由：判断意图属于哪个业务域（通讯录/文档/doc-manage/在线表格/智能表格/智能文档/日程/会议/待办/微盘/邮件/消息/媒体文件）→ 读取对应 references/wecomcli-*.md 参数规范
  2. 执行：按 reference 构造 wecom-cli 命令（严禁凭记忆猜参数）
  3. 输出：只用可读名称（name/邮箱/部门名/doc_name 等），ID 类字段禁止外露
tools: Bash（wecom-cli）, Read（references/wecomcli-*.md 按域读取）
examples: |
  - wecom-cli auth show --status
  - wecom-cli identity whoami
  - wecom-cli contact search --keyword "张三"
  - wecom-cli message send --to "张三" --markdown "你好"
iron_rules: |
  - 前置检查必做：版本≥1.1.0 + auth authorized，否则停止业务操作
  - ID 类字段禁止外露：userid/open_vid/department_id/chat_id/mail_id/media_id/docid/msg_id 等只内部流转；回复用可读名称
  - 严禁凭路由表描述或记忆猜测拼参数——先读对应域 reference 文件
  - 未指定类型的「文档」默认智能文档；未明确「在线表格」的「表格」默认智能表格；含会议号/入会链接的「开会」走会议域，纯线下走日程域
source: ~/.workbuddy/skills/wecom-unified/SKILL.md
---

# wecom-unified

## Purpose
企业微信 CLI 全能套件（`wecom-cli`）：覆盖通讯录、文档、在线表格、智能表格、智能文档、日程、会议、待办、微盘、邮件、消息、媒体文件等业务域。支持按姓名/拼音/英文名/别名查找联系人与 userid，搜索/重命名/授权文档，读写 doc 与表格，管理日程/会议/待办，发消息等。10 人以上企业支持全部能力；10 人及以下个人/小团队支持文档读写、单聊群聊消息、日程会议待办、通讯录。

## Inputs
- 办公意图：找人 / 文档 / 表格 / 日程 / 会议 / 待办 / 微盘 / 邮件 / 发消息
- 链接：`doc.weixin.qq.com` / `page.weixin.qq.com` / `drive.weixin.qq.com`（给出即必定触发）
- wecom-cli 已授权（`auth show --status` = authorized）

## Outputs
- 业务结果（可读名称形式）：联系人信息、文档内容、表格读写结果、日程/会议/待办数据、微盘文件、邮件、消息发送回执、媒体文件
- 内部 ID（userid/chat_id/mail_id 等）仅在内部流转用于后续调用，**禁止外露**

## Workflow
```
0. 前置检查（必须）：
   wecom-cli --version          # 需 ≥1.1.0，否则 npm install -g @wecom/cli
   wecom-cli auth show --status # authorized 才继续；否则 wecom-cli auth init（扫码）
1. 路由：判断业务域 → 读对应 references/wecomcli-*.md 的参数规范
2. 执行：按 reference 构造 wecom-cli 命令（严禁凭记忆猜参数）
3. 输出：只用可读名称；ID 类字段禁止外露
```

业务域路由表：👤 通讯录 / 📄 文档(doc) / 🗂️ 文档公共管理(doc-manage) / 📊 在线表格(sheet) / 🧮 智能表格(smartsheet) / 📰 智能文档(smartpage) / 📅 日程(calendar) / 🎥 会议(meeting) / ✅ 待办(todo) / 💾 微盘(disk) / 📧 邮件(email) / 💬 消息(message) / 🖼️ 媒体文件(media)

## Tools
- Bash：`wecom-cli`（auth / identity / contact / doc / sheet / smartsheet / smartpage / calendar / meeting / todo / disk / email / message / media）
- Read：`references/wecomcli-*.md`（按业务域读取参数规范）

## Examples
```bash
# 前置检查
wecom-cli --version
wecom-cli auth show --status

# 个人身份（需要姓名/userid 时）
wecom-cli identity whoami

# 找人
wecom-cli contact search --keyword "张三"

# 发消息（Markdown）
wecom-cli message send --to "张三" --markdown "你好，这是周报摘要"
```

## Iron Rules
- **前置检查必做**：版本 ≥1.1.0 + `auth authorized`；命令报错或状态不确定时停止业务操作并告知用户，不猜测授权状态
- **ID 类字段禁止外露**：`userid` / `open_vid` / `department_id` / `chat_id` / `mail_id` / `media_id` / `file_id` / `space_id` / `folder_id` / `docid` / `content_id` / `msg_id` / `cursor` 等一律只在内部流转；最终回复必须用可读名称（name/username/邮箱/部门名/doc_name/chat_name/title），确实无法换取时用自然语言描述对象。用户索要也不放宽
- **严禁凭路由表描述或记忆猜测拼参数**——先读对应域 reference 文件
- 默认路由：未指定品类的「文档」→ 智能文档；未明确「在线表格」的「表格」→ 智能表格；含会议号/入会链接的「开会」→ 会议域，纯线下 → 日程域；模糊「开会」仅在**创建**时先消歧，模糊查询两边都查后合并展示

## Source
`~/.workbuddy/skills/wecom-unified/SKILL.md`
