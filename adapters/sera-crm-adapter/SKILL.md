---
name: sera-crm-adapter
version: 1.0.0
author: Sera
category: adapters
status: active
compatible:
  - WorkBuddy
  - Codex
  - Trae
  - Claude-Code
  - Cursor
---

# sera-crm-adapter

## Purpose
CRM 适配层：客户档案、跟进记录、交易记录的统一管理接口。连接外部 CRM 数据源（多维表格 / 表格 / 自建库），为 otc-agent 提供客户数据读写能力。

## When to use
- 「这个客户之前聊过什么」
- 「记录这个客户的跟进」
- 「列出今天的待跟进客户」
- 「更新客户状态 / 标签」

## Inputs
- 客户信息（姓名/公司/联系方式/需求/来源）
- 跟进记录（时间/方式/内容/结果）
- 交易记录（品项/金额/状态/风险标记）
- 查询条件（按状态/标签/时间/关键词）

## Outputs
- 客户档案（结构化：画像/历史/标签）
- 跟进时间线（可回溯）
- 待办提醒（今天该跟进的客户）
- 交易/风险记录

## Workflow
```
1. 定位数据源（CRM 存储位置，见 Dependencies）
2. 读：按条件查客户 → 返回结构化档案
3. 写：新增/更新客户、跟进、交易记录
4. 提醒：按跟进计划筛选今日待办
5. 风险标记：命中风控红线 → 标记并升级
6. 与 sera-memory-system 双写（CRM 记事实，Memory 记决策）
```

## 数据模型
```yaml
customer:
  id: <internal>
  name: <名称>            # 可读名，不外露内部 ID
  company: <公司>
  contacts: [<邮箱/手机/微信>]
  tags: [<标签>]
  status: <new|active|negotiating|won|lost|blocked>
  source: <来源>
  created_at: <日期>

followup:
  customer_id: <id>
  at: <时间>
  method: <邮件|企微|电话|会议>
  content: <摘要>
  result: <pending|replied|no_response>

deal:
  customer_id: <id>
  item: <品项>
  amount: <金额>
  status: <inquiry|quote|accepted|rejected|executed>
  risk: <none|watch|high>
```

## Dependencies
- 存储后端（任选其一，当前建议多维表格 / 本地 sqlite）：
  - 飞书多维表格（lark-base，平台依赖）
  - 企业微信智能表格（wecom，平台依赖）
  - 本地 SQLite/JSON（`~/SeraContextHub/` 业务数据区）
- `sera-memory-system`（决策记忆，双写）

## Examples
- 「查一下客户张三的状态」→ 返回客户档案
- 「记录今天的跟进：报价已发」→ 写 followup + 更新 deal
- 「今天该跟进谁」→ 按 followup 计划筛选
