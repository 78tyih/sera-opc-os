# Sera Design Template Library

> 将真实项目沉淀为可复用、可调用、可展示、可商品化的设计资产。

## 1. 定位

Sera Design Template Library 是 `sera-design-intelligence` 的商业化与复用层。

它不保存“好看的截图”，而是把已经验证过的真实项目拆成四层资产：

1. **Case Study** — 真实项目、真实问题、真实约束、真实结果。
2. **Style / Design DNA** — 视觉语言、tokens、组件规律、交互原则。
3. **Reusable Template** — 去品牌、去业务敏感信息后，可直接替换数据/内容使用的模板。
4. **Agent Skill** — Agent 可执行的设计与信息架构规则。

核心循环：

`Real Project → Case Study → Style DNA → Template → Skill → New Project → Review → Improve`

---

## 2. 首批正式模板

### A. Regulated Deal Desk

来源：HTX OTC Landing Page

用途：
- Fintech / OTC / Financial Service
- High-trust / regulated service
- Institutional service landing
- High-value lead generation

核心价值：
- 先建立信任，再解释服务
- 先讲边界与合规，再进入转化
- 将复杂交易/服务流程拆成低认知负担的页面结构

推荐 Design DNA：`sera-fintech-premium`

### B. Execution Command Center

来源：HTX OTC Progress Hub

用途：
- Project execution dashboard
- Founder / management command center
- Client delivery portal
- Sales / BD pipeline dashboard
- AI project progress dashboard

核心价值：
- 让管理者 30 秒内读懂项目状态
- 强制呈现：Goal / Progress / Blocker / Next / Ask
- 将工作系统的数据压缩成 management presentation layer

推荐 Design DNA：`sera-operations-dashboard`

---

## 3. 标准资产包结构

每个 Template Pack 建议包含：

```text
template-name/
├── README.md              # 产品定位、用户、使用场景
├── SKILL.md               # Agent 执行规则
├── DESIGN_SYSTEM.md       # Design DNA / Tokens / Components
├── INFORMATION_ARCH.md    # 页面和信息架构
├── DATA_SCHEMA.md         # 数据接口/JSON Schema（如适用）
├── demo.html              # 脱敏 Demo
├── prompts/
│   └── generate.md        # 生成提示词
└── examples/
    └── example-project.md
```

---

## 4. 商品化层级

### Style Pack
设计语言、tokens、组件规则、motion、prompt。

### Template Pack
可运行 Demo + 信息结构 + 可替换内容规范。

### Skill Pack
AI Agent 可直接执行的 SKILL.md。

### Solution Pack
Template + Skill + Data Schema + Integration Guide + Demo。

---

## 5. 统一抽取工作流

以后每一个完成度高、值得复用的项目都执行：

1. **Find** — 识别值得沉淀的真实项目。
2. **Extract** — 提取布局、视觉、组件、交互、内容策略。
3. **Abstract** — 删除品牌专属和业务敏感部分，抽象通用规律。
4. **Register Style** — 更新 `styles/registry.json`。
5. **Package Template** — 形成可运行模板。
6. **Write Skill** — 形成 Agent 可执行规则。
7. **Generate Demo** — 用完全不同的业务场景验证可迁移性。
8. **Review** — 检查是否真的可复用，而不是仅仅“换皮”。
9. **Publish / Sell / Reuse** — 内部调用或对外商品化。

---

## 6. 质量门槛

一个项目只有满足以下条件才进入 Template Library：

- 已有真实使用场景或真实项目验证；
- 至少有 3 个可跨项目复用组件；
- 信息架构能够脱离原品牌独立成立；
- 替换品牌和业务内容后仍能保持设计价值；
- 有明确目标用户和问题，而不是纯视觉展示；
- 能写成 Agent 可执行规则；
- Demo 不包含原项目敏感信息。

---

## 7. 核心原则

> **Project is evidence. Style is abstraction. Template is product. Skill is execution.**

Sera Design Intelligence 的目标不是收藏设计，而是让每一个优秀项目都成为下一次生产的加速器。