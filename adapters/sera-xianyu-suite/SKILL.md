---
name: sera-xianyu-suite
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

# sera-xianyu-suite

## Purpose
闲鱼卖家平台适配层：把闲鱼消息监听、AI 客服、议价、会话上下文与卖家运营能力接入 Sera OPC OS。第一阶段以 `shaxiu/XianyuAutoAgent` 作为外部 Runtime，不复制其 GPL-3.0 源码到本仓库。

## When to use
- 「帮我接管闲鱼客服 / 自动回复闲鱼消息」
- 「这个买家在砍价，按我的底价策略回复」
- 「总结今天闲鱼买家的咨询和成交线索」
- 「把闲鱼聊天沉淀到 CRM / Memory」
- 「准备闲鱼商品文案 / 上架草稿」
- 「检查闲鱼 Runtime 是否在线」

## Inputs
- 闲鱼账号运行态：Cookie / Session（仅通过本地 `.env`、Secret Store 或受控 Runtime 注入，禁止写入 Git）
- 商品事实：标题、描述、售价、底价、库存、交付方式
- 客服策略：语气、议价空间、禁止承诺、人工升级条件
- LLM 配置：OpenAI-compatible Base URL、Model、API Key
- 可选商品发布参数：图片、分类、位置、发布时间

## Outputs
- 买家意图分类：咨询 / 议价 / 技术问题 / 售后 / 风险
- 建议回复或自动回复结果
- 议价决策：接受 / 还价 / 拒绝 / 转人工
- 会话摘要、客户线索、商品兴趣标签
- 商品标题 / 描述 / 定价建议 / 上架草稿
- Runtime 健康状态与异常告警

## Runtime Architecture

```text
User / Sera Agent
       ↓
sera-xianyu-suite
       ├── Message & Session Adapter
       │      ↓
       │   shaxiu/XianyuAutoAgent (external GPL-3.0 runtime)
       │      ├── XianyuApis.py        # 闲鱼协议/消息层
       │      ├── context_manager.py   # 会话上下文
       │      ├── XianyuAgent.py       # 分类/议价/客服 Agent
       │      └── main.py              # WebSocket 常驻监听
       │
       ├── sera-crm-adapter            # 客户/跟进/成交线索
       ├── sera-memory-system           # 长期决策与经验
       └── sera-browser-automation      # 商品发布等浏览器动作（独立门控）
```

## Capability Map

| Capability | V1 状态 | 执行层 |
|---|---|---|
| 闲鱼消息监听 | active | XianyuAutoAgent |
| AI 自动回复 | active | XianyuAutoAgent |
| 上下文会话 | active | XianyuAutoAgent |
| 智能议价 | active | XianyuAutoAgent |
| 技术/默认客服路由 | active | XianyuAutoAgent |
| CRM / Memory 沉淀 | active | Sera adapters/core |
| 商品文案生成 | active | Sera LLM |
| 自动创建/发布商品 | gated | sera-browser-automation / 可插拔 publisher runtime |
| 自动改价/删除商品 | gated | browser automation / publisher runtime |
| 支付、退款、账户安全操作 | human-only | 禁止无人值守执行 |

> 注意：`shaxiu/XianyuAutoAgent` 的主能力是消息监听、AI 客服、上下文与议价，不把“自动上架商品”误报为其原生能力。发布动作作为独立能力接入。

## Workflow

```text
1. Runtime Health Check
   └─ 检查闲鱼 Session / Cookie / WebSocket / LLM
2. Receive Buyer Message
   └─ 拉取商品与会话上下文
3. Intent Router
   ├─ 普通咨询 → Default Agent
   ├─ 议价 → Price Agent + 底价策略
   ├─ 技术问题 → Tech Agent
   └─ 高风险/异常 → Human Escalation
4. Response Gate
   ├─ 低风险客服 → 可自动发送
   └─ 金额/承诺/售后/敏感动作 → 人工确认
5. Persist
   ├─ CRM：客户、商品兴趣、跟进状态
   └─ Memory：有效话术、议价结果、异常案例
6. Optional Listing Flow
   └─ 生成草稿 → 人工确认 → browser/publisher 执行 → 截图/结果验证
```

## External Runtime
- Primary upstream: `shaxiu/XianyuAutoAgent`
- Pinned baseline commit: `540bbc26cf02ee6348d997843942776a9be9460b` (2026-06-10)
- License: GPL-3.0
- Integration mode: **external process / container boundary**。不将上游源码复制或合并到 Sera OPC OS。

上游环境变量基线：

```dotenv
API_KEY=<secret>
COOKIES_STR=<secret>
MODEL_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-max
TOGGLE_KEYWORDS=。
SIMULATE_HUMAN_TYPING=False
```

这些变量只能存在于运行机器的 Secret Store / `.env`，不得提交真实值。

## Dependencies
- `adapters/sera-browser-automation` — 商品发布、页面动作与最终验证
- `adapters/sera-crm-adapter` — 客户/询盘/跟进沉淀
- `core/sera-memory-system` — 决策、经验、偏好长期记忆
- 外部 Runtime：`shaxiu/XianyuAutoAgent`
- Docker 或 Python 运行环境

## Iron Rules
1. **禁止提交 Cookie / API Key / Token / 登录态。**
2. **默认不自动执行支付、退款、账户安全、删除商品等不可逆动作。**
3. **自动议价必须配置底价；未配置底价时只能建议回复，不能承诺成交价。**
4. **商品发布 V1 默认 Human-in-the-loop：先生成草稿，确认后再执行。**
5. **发送/发布后必须二次验证结果，不把“点击成功”当作“业务成功”。**
6. **上游采用非官方闲鱼协议/自动化方式，平台变更可能导致失效或账号风控；异常时立即降级到人工模式。**
7. **GPL 边界清晰：Sera 仅保存适配规范、配置和调用契约，上游源码独立部署。**

## Examples
- 「把闲鱼客服打开，普通咨询自动回复，低于 300 元的还价一律不要答应。」
- 「总结今天闲鱼上所有买家最常问的问题，并沉淀到客服知识库。」
- 「为这台二手显示器生成闲鱼标题、描述和价格建议，但先不要发布。」
- 「准备上架这 5 个商品，先给我草稿和风险检查，确认后再走发布。」
