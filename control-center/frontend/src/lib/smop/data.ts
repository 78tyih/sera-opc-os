// SMOP 数据桥 — 真实数据源 + spec 状态夹具
//
// 数据来源与诚实标记（dataSource）：
//   registry      来自 registry/*.json（真实注册表）
//   agent-yaml    来自 agents/*/agent.yaml（真实员工契约）
//   constitution  来自 constitution/company-constitution.md（真实公司宪法）
//   spec          来自 architecture/v2/*.md 的协议示例（spec 状态数据，用于“顶”尚未落地的 Memory Engine）
//
// 关键原则：不伪造记忆。Decision / Experience / Rule 目前只有 spec 样例，
// 因此明确标记为 "spec"，并在 UI 中以徽标区分，不冒充真实积累的记忆。

import type { DataSource, ObjectType, Relation, RelationType, SMOPObject } from "./types"

export type { SMOPObject }

function R(source: string, relation: RelationType, target: string, weight = 0.8): Relation {
  return { source, relation, target, weight }
}

interface MakeArgs {
  type: ObjectType
  name: string
  description?: string
  status?: SMOPObject["status"]
  importance?: number
  confidence?: number
  owner?: string
  dataSource: DataSource
  properties?: Record<string, any>
  relations?: Relation[]
}

function make(id: string, a: MakeArgs): SMOPObject {
  return {
    id,
    type: a.type,
    name: a.name,
    description: a.description ?? "",
    status: a.status ?? "active",
    importance: a.importance ?? 0.6,
    confidence: a.confidence ?? 1,
    owner: a.owner ?? "person.sera",
    dataSource: a.dataSource,
    properties: a.properties ?? {},
    relations: a.relations ?? [],
  }
}

// ---------- Person / Company ----------

const personSera = make("person.sera", {
  type: "Person",
  name: "Sera",
  description: "公司创始人（人类 CEO）",
  importance: 1,
  confidence: 1,
  dataSource: "constitution",
  properties: { role: "Founder", responsibilities: ["愿景", "品味", "战略决策", "资本配置", "品牌原则"] },
  relations: [R("person.sera", "owns", "company.sera", 1)],
})

const companySera = make("company.sera", {
  type: "Company",
  name: "Sera AI Company",
  description: "AI 原生公司",
  importance: 1,
  confidence: 1,
  dataSource: "constitution",
  properties: { industry: "Fintech + AI", headquarters: "Remote", founded: "2026" },
  relations: [R("company.sera", "owned_by", "person.sera", 1)],
})

// ---------- Agents（registry/agents.json 真实数据） ----------

const agents: SMOPObject[] = [
  make("agent.ceo", {
    type: "Agent",
    name: "CEO Agent",
    description: "最高决策层 — 商业评估、资源分配、优先级管理",
    importance: 1,
    dataSource: "registry",
    properties: { role: "Chief Executive Agent", type: "executive", model: "Claude / DeepSeek" },
    relations: [
      R("agent.ceo", "uses_skill", "skill.decision-framework", 1),
      R("agent.ceo", "uses_skill", "skill.priority-engine", 1),
      R("agent.ceo", "uses_skill", "skill.project-profile", 0.9),
      R("agent.ceo", "uses_skill", "skill.market-research", 0.8),
      R("agent.ceo", "uses_skill", "skill.product-analysis", 0.8),
    ],
  }),
  make("agent.product", {
    type: "Agent",
    name: "Product Agent",
    description: "产品发布专家 — 从模糊想法到结构化发布资产",
    importance: 0.85,
    dataSource: "registry",
    properties: { role: "Product Expert", type: "domain-expert", model: "DeepSeek" },
    relations: [
      R("agent.product", "reports_to", "agent.ceo", 0.9),
      R("agent.product", "uses_skill", "skill.project-profile", 1),
      R("agent.product", "uses_skill", "skill.product-analysis", 1),
      R("agent.product", "uses_skill", "skill.market-research", 1),
      R("agent.product", "uses_skill", "skill.user-persona", 0.9),
      R("agent.product", "uses_skill", "skill.positioning", 0.9),
      R("agent.product", "uses_skill", "skill.copywriting", 0.8),
      R("agent.product", "uses_skill", "skill.product-manual", 0.7),
    ],
  }),
  make("agent.design", {
    type: "Agent",
    name: "Design Agent",
    description: "设计专家 — 品牌、视觉、UI",
    importance: 0.85,
    dataSource: "registry",
    properties: { role: "Design Director", type: "domain-expert", model: "Trae / Codex" },
    relations: [
      R("agent.design", "reports_to", "agent.ceo", 0.9),
      R("agent.design", "uses_skill", "skill.design-studio", 1),
      R("agent.design", "uses_skill", "skill.design-intelligence", 1),
      R("agent.design", "uses_skill", "skill.asset-manager", 0.9),
      R("agent.design", "uses_skill", "skill.figma-review", 0.9),
      R("agent.design", "uses_skill", "skill.htx-style", 0.8),
    ],
  }),
  make("agent.video", {
    type: "Agent",
    name: "Video Agent",
    description: "视频内容专家 — 脚本、故事板、素材（最成熟）",
    importance: 0.8,
    dataSource: "registry",
    properties: { role: "Video Producer", type: "domain-expert", model: "Codex / Serawin" },
    relations: [
      R("agent.video", "reports_to", "agent.ceo", 0.9),
      R("agent.video", "uses_skill", "skill.video-pipeline", 1),
      R("agent.video", "uses_skill", "skill.content-factory", 1),
    ],
  }),
  make("agent.propfirm", {
    type: "Agent",
    name: "PropFirm Agent",
    description: "PropFirm 行业专家 — 情报、竞品、内容",
    importance: 0.8,
    dataSource: "registry",
    properties: { role: "PropFirm Industry Intelligence", type: "domain-expert", model: "DeepSeek" },
    relations: [
      R("agent.propfirm", "reports_to", "agent.ceo", 0.9),
      R("agent.propfirm", "uses_skill", "skill.intelligence-monitor", 1),
      R("agent.propfirm", "uses_skill", "skill.content-factory", 0.9),
      R("agent.propfirm", "uses_skill", "skill.browser-automation", 0.9),
    ],
  }),
  make("agent.otc", {
    type: "Agent",
    name: "OTC Agent",
    description: "OTC 商务专家 — 客户分析、报价、跟进、风险判断",
    importance: 0.75,
    dataSource: "registry",
    properties: { role: "OTC Trading & Client Management", type: "domain-expert", model: "DeepSeek" },
    relations: [
      R("agent.otc", "reports_to", "agent.ceo", 0.9),
      R("agent.otc", "uses_skill", "skill.crm-adapter", 1),
      R("agent.otc", "uses_skill", "skill.mail-hub", 1),
    ],
  }),
  make("agent.trading", {
    type: "Agent",
    name: "Trading Agent",
    description: "交易研究专家 — 复盘、策略、订单流解读",
    importance: 0.75,
    dataSource: "registry",
    properties: { role: "Trading Research & Analysis", type: "domain-expert", model: "DeepSeek" },
    relations: [
      R("agent.trading", "reports_to", "agent.ceo", 0.9),
      R("agent.trading", "uses_skill", "skill.trading-analysis", 1),
    ],
  }),
  make("agent.design-dept", {
    type: "Agent",
    name: "Design Department",
    description: "设计部门 — 6 个子 Agent 组合（research/extraction/generator/system/review/asset）",
    importance: 0.7,
    dataSource: "registry",
    properties: {
      type: "department",
      subAgents: [
        "design-research-agent",
        "design-extraction-agent",
        "design-generator-agent",
        "design-system-agent",
        "design-review-agent",
        "asset-manager-agent",
      ],
    },
    relations: [R("agent.design-dept", "manages", "agent.design", 0.9)],
  }),
]

// ---------- Projects（registry/projects.json 真实数据） ----------

const projects: SMOPObject[] = [
  make("project.htx-otc", {
    type: "Project", name: "HTX OTC", description: "火币 OTC 场外交易 — 落地页与进度中心",
    status: "active", importance: 0.9, dataSource: "registry",
    properties: { category: "business", repos: ["78tyih/htx-otc-landing", "78tyih/htx-otc-progress-hub"], agent: "otc-agent" },
    relations: [R("project.htx-otc", "belongs_to", "company.sera", 1)],
  }),
  make("project.propfirm-tv", {
    type: "Project", name: "PropFirm.TV", description: "PropFirm 考试盘视频内容平台",
    status: "active", importance: 0.9, dataSource: "registry",
    properties: { category: "content", repos: ["78tyih/propfirm-tv", "78tyih/propfirm-tv-video-factory"], agent: "propfirm-agent" },
    relations: [R("project.propfirm-tv", "belongs_to", "company.sera", 1)],
  }),
  make("project.poff-trading", {
    type: "Project", name: "泡芙交易 Poff Trading", description: "期货考试盘折扣、工具与社区平台",
    status: "active", importance: 0.7, dataSource: "registry",
    properties: { category: "business", repos: ["78tyih/poff-trading"], agent: "propfirm-agent" },
    relations: [R("project.poff-trading", "belongs_to", "company.sera", 1)],
  }),
  make("project.deltapex", {
    type: "Project", name: "Deltapex / 德湃", description: "德湃考试盘 — 官网、品牌、满意度调研",
    status: "active", importance: 0.7, dataSource: "registry",
    properties: { category: "business", repos: ["78tyih/deltapex-site"], agent: "propfirm-agent" },
    relations: [R("project.deltapex", "belongs_to", "company.sera", 1)],
  }),
  make("project.traderbti", {
    type: "Project", name: "Trader BTI", description: "Trader BTI 交易平台",
    status: "active", importance: 0.6, dataSource: "registry",
    properties: { category: "business", repos: ["78tyih/traderbti"], agent: "trading-agent" },
    relations: [R("project.traderbti", "belongs_to", "company.sera", 1)],
  }),
  make("project.trader-dna", {
    type: "Project", name: "Trader DNA", description: "交易性格画像测评 — 私域引流工具",
    status: "active", importance: 0.6, dataSource: "registry",
    properties: { category: "business", repos: ["78tyih/Trader-DNA"], agent: "trading-agent" },
    relations: [R("project.trader-dna", "belongs_to", "company.sera", 1)],
  }),
  make("project.ququ", {
    type: "Project", name: "蛐蛐 QuQu", description: "中文语音输入工具 — 浮窗波形、AI 提示词提炼",
    status: "active", importance: 0.5, dataSource: "registry",
    properties: { category: "tool", repos: ["78tyih/ququ"] },
    relations: [R("project.ququ", "belongs_to", "company.sera", 1)],
  }),
  make("project.knowledgestar", {
    type: "Project", name: "KnowledgeStar Galaxy", description: "Obsidian 笔记知识星系可视化",
    status: "active", importance: 0.5, dataSource: "registry",
    properties: { category: "tool", repos: ["78tyih/knowledgestar-galaxy"] },
    relations: [R("project.knowledgestar", "belongs_to", "company.sera", 1)],
  }),
  make("project.clone-website", {
    type: "Project", name: "Clone Website", description: "网站克隆工具",
    status: "active", importance: 0.4, dataSource: "registry",
    properties: { category: "tool", repos: ["78tyih/clone-website"] },
    relations: [R("project.clone-website", "belongs_to", "company.sera", 1)],
  }),
  make("project.sera-agent-console", {
    type: "Project", name: "Sera OPC OS Control Center", description: "Sera OPC OS 控制中心 WebUI（本前端）",
    status: "active", importance: 0.9, dataSource: "registry",
    properties: { category: "infrastructure", repos: [], agent: "core" },
    relations: [R("project.sera-agent-console", "belongs_to", "company.sera", 1)],
  }),
  make("project.niuniu-ai", {
    type: "Project", name: "牛牛 AI", description: "AI 教育平台（待启动）",
    status: "draft", importance: 0.5, dataSource: "registry",
    properties: { category: "product" },
    relations: [R("project.niuniu-ai", "belongs_to", "company.sera", 1)],
  }),
  make("project.tradespan", {
    type: "Project", name: "TradeSpan", description: "MT4/MT5 交易软件（待启动，连接 ATAS 与 MT4）",
    status: "draft", importance: 0.8, dataSource: "registry",
    properties: { category: "product", goal: "连接 ATAS 和 MT4 的交易平台", department: "Engineering" },
    relations: [R("project.tradespan", "belongs_to", "company.sera", 1)],
  }),
]

// ---------- Skills（registry/skills.json 真实数据） ----------

const skillDefs: Array<[string, string, string, string?]> = [
  // [id, name, purpose, owner]
  ["decision-framework", "Decision Framework", "CEO 商业决策评估框架", "agent.ceo"],
  ["priority-engine", "Priority Engine", "项目优先级评分与资源分配", "agent.ceo"],
  ["project-profile", "Project Profile", "模糊想法→结构化项目文档", "agent.product"],
  ["product-analysis", "Product Analysis", "产品理解与分析", "agent.product"],
  ["market-research", "Market Research", "市场研究与竞品分析", "agent.product"],
  ["user-persona", "User Persona", "用户画像创建", "agent.product"],
  ["positioning", "Positioning", "产品定位与差异化", "agent.product"],
  ["copywriting", "Copywriting", "专业文案撰写", "agent.product"],
  ["product-manual", "Product Manual", "产品手册生成", "agent.product"],
  ["intelligence-monitor", "Intelligence Monitor", "PropFirm 商业情报收集", "agent.propfirm"],
  ["content-factory", "Content Factory", "官网资产工厂", "agent.propfirm"],
  ["trading-analysis", "Trading Analysis", "交易复盘、策略分析", "agent.trading"],
  ["design-intelligence", "Design Intelligence", "设计智能 — 风格/案例/参考库", "agent.design"],
  ["design-studio", "Design Studio", "品牌、视觉、UI 生成", "agent.design"],
  ["video-pipeline", "Video Pipeline", "视频生产流水线", "agent.video"],
  ["asset-manager", "Asset Manager", "素材管理", "agent.design"],
  ["figma-review", "Figma Review", "Figma 设计审查", "agent.design"],
  ["browser-automation", "Browser Automation", "浏览器自动化", "agent.propfirm"],
  ["crm-adapter", "CRM Adapter", "CRM 适配器", "agent.otc"],
  ["lark-suite", "Lark Suite", "飞书套件适配器", "core"],
  ["macos-ui", "macOS UI", "macOS 界面自动化", "core"],
  ["mail-hub", "Mail Hub", "邮件中心适配器", "agent.otc"],
  ["wecom-suite", "WeCom Suite", "企业微信套件适配器", "core"],
  ["kimi-style", "Kimi Design Style", "Kimi 设计风格参照", "agent.design"],
  ["htx-style", "HTX Design Style", "HTX 金融蓝/OC/暗色 设计参照", "agent.design"],
  ["svg-sketch", "SVG Sketch Workbench", "SVG 原型/UI 草图", "agent.design"],
]

const skills: SMOPObject[] = skillDefs.map(([id, name, purpose, owner]) =>
  make(`skill.${id}`, {
    type: "Skill",
    name,
    description: purpose,
    importance: 0.7,
    confidence: 0.95,
    owner: owner ?? "system",
    dataSource: "registry",
    properties: { category: "skill" },
  }),
)

// ---------- Workflows（registry/workflows.json 真实数据） ----------

const workflows: SMOPObject[] = [
  make("workflow.product-init", {
    type: "Workflow", name: "Product Init Workflow", description: "产品初始化 — 从模糊想法到结构化项目文档",
    importance: 0.8, dataSource: "registry",
    properties: { trigger: "产品发布/项目初始化", steps: 7, source: "core/sera-agent-router/workflows/product-init.yaml" },
    relations: [R("workflow.product-init", "managed_by", "agent.product", 0.9)],
  }),
  make("workflow.product-analysis", {
    type: "Workflow", name: "Product Analysis Workflow", description: "快速产品分析 — 理解与研究",
    importance: 0.7, dataSource: "registry",
    properties: { trigger: "产品分析/市场研究", steps: 2, source: "core/sera-agent-router/workflows/product-analysis.yaml" },
    relations: [R("workflow.product-analysis", "managed_by", "agent.product", 0.9)],
  }),
  make("workflow.product-factory-pipeline", {
    type: "Workflow", name: "Product Factory Pipeline", description: "完整产品发布流水线 — 产品+设计+视频+审查",
    importance: 0.85, dataSource: "registry",
    properties: { trigger: "产品发布页/官网/落地页", steps: 8, source: "core/sera-agent-router/routes.yaml" },
    relations: [
      R("workflow.product-factory-pipeline", "managed_by", "agent.ceo", 0.9),
      R("workflow.product-factory-pipeline", "uses_skill", "skill.project-profile", 0.8),
      R("workflow.product-factory-pipeline", "uses_skill", "skill.design-studio", 0.8),
    ],
  }),
  make("workflow.page-product-launch", {
    type: "Workflow", name: "Page Product Launch", description: "产品发布页 — 素材+设计+视频+审查",
    importance: 0.8, dataSource: "registry",
    properties: { trigger: "发布页/产品页/网站", steps: 4, source: "core/sera-agent-router/workflows/product-launch-page.yaml" },
    relations: [R("workflow.page-product-launch", "managed_by", "agent.product", 0.85)],
  }),
  make("workflow.propfirm-video", {
    type: "Workflow", name: "PropFirm Video Workflow", description: "PropFirm 视频生产工作流",
    importance: 0.8, dataSource: "registry",
    properties: { trigger: "视频/短视频/口播", steps: 4, source: "core/sera-agent-router/workflows/propfirm-video.yaml" },
    relations: [
      R("workflow.propfirm-video", "managed_by", "agent.video", 0.9),
      R("workflow.propfirm-video", "uses_skill", "skill.video-pipeline", 0.9),
    ],
  }),
]

// ---------- Decisions（spec 状态的协议示例数据） ----------

const decisions: SMOPObject[] = [
  make("decision.tradespan.dark-ui", {
    type: "Decision", name: "TradeSpan 暗色金融科技 UI", description: "TradeSpan 采用暗色金融科技风格作为设计语言",
    status: "active", importance: 0.9, confidence: 1, dataSource: "spec",
    properties: {
      context: "TradeSpan 官网重新设计",
      decision: "采用暗色金融科技风格 (Dark Fintech Style)",
      reason: "增强交易者信任感，符合行业审美",
      alternatives: ["亮色商务风", "极简白"],
      constraints: ["主黑 #05070A", "主题蓝 #146EFF", "避免大面积渐变"],
    },
    relations: [
      R("decision.tradespan.dark-ui", "applies_to", "project.tradespan", 1),
      R("decision.tradespan.dark-ui", "supersedes", "decision.tradespan.light-ui", 0.8),
    ],
  }),
  make("decision.tradespan.light-ui", {
    type: "Decision", name: "TradeSpan 亮色 UI（已废弃）", description: "早期拟采用亮色商务风",
    status: "replaced", importance: 0.3, confidence: 1, dataSource: "spec",
    properties: { decision: "亮色商务风", reason: "通用安全但不够可信" },
    relations: [R("decision.tradespan.light-ui", "applies_to", "project.tradespan", 0.5)],
  }),
  make("decision.video.react-gsap", {
    type: "Decision", name: "金融视频用 React+GSAP 而非纯 AI 生成", description: "为保证 UI 可信度，用真实前端动效+录屏拼接",
    status: "active", importance: 0.85, confidence: 0.9, dataSource: "spec",
    properties: {
      decision: "改用 React + GSAP 生成前端动效 + 录屏拼接",
      reason: "纯 AI 视频生成无法精确控制 UI 元素",
    },
    relations: [R("decision.video.react-gsap", "applies_to", "project.propfirm-tv", 1)],
  }),
  make("decision.htx-otc.dark-financial", {
    type: "Decision", name: "HTX OTC 暗色金融风 + 信任优先", description: "HTX OTC 沿用暗色金融科技设计语言",
    status: "active", importance: 0.8, confidence: 1, dataSource: "spec",
    properties: {
      decision: "暗色金融风，主黑 + 品牌蓝，图形主导",
      reason: "可信度 > 炫技，符合 HTX 品牌",
      constraints: ["主黑 #05070A", "主题蓝 #146EFF", "强调红 #FF3B45"],
    },
    relations: [R("decision.htx-otc.dark-financial", "applies_to", "project.htx-otc", 1)],
  }),
  make("decision.design.htx-brand", {
    type: "Decision", name: "Sera OPC OS 品牌采用 HTX 金融蓝", description: "控制中心与产品统一采用 HTX 品牌语言",
    status: "active", importance: 0.9, confidence: 1, dataSource: "constitution",
    properties: {
      decision: "品牌蓝 #0066FF + 深色底 + 克制编辑风",
      reason: "品牌一致性与易读性，冷静金融编辑风",
      constraints: ["主蓝 #0066FF", "避免霓虹/赛博/大渐变"],
    },
    relations: [
      R("decision.design.htx-brand", "applies_to", "project.sera-agent-console", 1),
      R("decision.design.htx-brand", "applies_to", "project.htx-otc", 0.8),
    ],
  }),
]

// ---------- Experiences（spec 状态的协议示例数据） ----------

const experiences: SMOPObject[] = [
  make("experience.video.ui-failure", {
    type: "Experience", name: "纯 AI 视频缺乏 UI 可信度", description: "尝试纯 AI 生成金融视频，结果缺乏真实 UI",
    status: "active", importance: 0.85, confidence: 0.95, dataSource: "spec",
    properties: {
      task: "生成金融产品宣传视频",
      result: "failed",
      rootCause: "AI 视频生成无法精确控制 UI 元素",
      resolution: "改用 React + GSAP 前端动效 + 录屏拼接",
      lesson: "金融产品视频必须有真实 UI 素材",
      costOfFailure: "3 天 + $200 API 费用",
    },
    relations: [
      R("experience.video.ui-failure", "related_to", "project.propfirm-tv", 0.9),
      R("experience.video.ui-failure", "led_to", "rule.financial.trust-first", 0.9),
      R("experience.video.ui-failure", "led_to", "decision.video.react-gsap", 0.8),
    ],
  }),
  make("experience.control-center.dual-frontend", {
    type: "Experience", name: "双前端导致部署与本地不一致", description: "静态 HTML 与 Next.js 双前端并存，Vercel 版本缺少按钮",
    status: "active", importance: 0.8, confidence: 0.9, dataSource: "spec",
    properties: {
      task: "Sera 控制中心上线",
      result: "failed",
      rootCause: "dashboard/public/index.html 与 control-center/frontend 并存，数据未统一",
      resolution: "统一到 control-center/frontend，以真实 registry 数据为唯一来源",
      lesson: "只保留一套前端入口，数据桥必须读真实注册表而非手写 mock",
    },
    relations: [
      R("experience.control-center.dual-frontend", "related_to", "project.sera-agent-console", 1),
      R("experience.control-center.dual-frontend", "led_to", "rule.org.system-over-individual", 0.7),
    ],
  }),
]

// ---------- Rules（constitution 真实 + spec 示例） ----------

const rules: SMOPObject[] = [
  make("rule.financial.trust-first", {
    type: "Rule", name: "金融产品可信优先原则", description: "金融产品内容中可信度 > 炫技",
    status: "active", importance: 0.95, confidence: 0.9, dataSource: "spec",
    properties: {
      content: "任何金融产品相关内容，必须优先考虑可信度。展示真实交易界面，避免纯 AI 生成内容。",
      priority: "high",
      scope: ["Video", "Landing Page", "Dashboard", "Marketing"],
      sourceExperiences: ["experience.video.ui-failure"],
    },
    relations: [
      R("rule.financial.trust-first", "derived_from", "experience.video.ui-failure", 1),
      R("rule.financial.trust-first", "applies_to", "project.propfirm-tv", 1),
      R("rule.financial.trust-first", "applies_to", "project.htx-otc", 1),
      R("rule.financial.trust-first", "applies_to", "project.tradespan", 1),
      R("rule.financial.trust-first", "applies_to", "project.deltapex", 0.9),
    ],
  }),
  make("rule.org.result-over-activity", {
    type: "Rule", name: "结果胜于活动", description: "每项任务必须与业务影响相关联",
    status: "active", importance: 0.9, confidence: 1, dataSource: "constitution",
    properties: { content: "每项任务必须与业务影响相关联，Agent 必须回答：这个任务如何创造业务价值？", priority: "high", scope: ["All"] },
    relations: [R("rule.org.result-over-activity", "applies_to", "company.sera", 1)],
  }),
  make("rule.org.system-over-individual", {
    type: "Rule", name: "系统胜于个人", description: "每次成功执行都应成为可复用系统",
    status: "active", importance: 0.9, confidence: 1, dataSource: "constitution",
    properties: { content: "每次成功必须沉淀为 Skill / Workflow / Template / Memory。", priority: "high", scope: ["All"] },
    relations: [R("rule.org.system-over-individual", "applies_to", "company.sera", 1)],
  }),
  make("rule.org.learning-over-repetition", {
    type: "Rule", name: "学习胜于重复", description: "每次失败都成为组织记忆",
    status: "active", importance: 0.9, confidence: 1, dataSource: "constitution",
    properties: { content: "每次失败都成为组织记忆，Experience → Lesson → 验证 3 次 → Rule。", priority: "high", scope: ["All"] },
    relations: [R("rule.org.learning-over-repetition", "applies_to", "company.sera", 1)],
  }),
  make("rule.org.quality-over-speed", {
    type: "Rule", name: "质量胜于速度", description: "每个 Factory 必须有 QC 门控",
    status: "active", importance: 0.85, confidence: 1, dataSource: "constitution",
    properties: { content: "每个 Factory 必须有 QC 门控（Human Approval Gate）。", priority: "medium", scope: ["Factory"] },
    relations: [R("rule.org.quality-over-speed", "applies_to", "company.sera", 1)],
  }),
  make("rule.org.compounding-knowledge", {
    type: "Rule", name: "复利知识胜于临时执行", description: "知识资产持续累积",
    status: "active", importance: 0.85, confidence: 1, dataSource: "constitution",
    properties: { content: "知识资产持续累积，避免一次性临时执行。", priority: "medium", scope: ["All"] },
    relations: [R("rule.org.compounding-knowledge", "applies_to", "company.sera", 1)],
  }),
]

// ---------- Assets（真实 repo 映射 + spec 示例） ----------

const assets: SMOPObject[] = [
  make("asset.htx-otc-landing", {
    type: "Asset", name: "HTX OTC Landing", description: "落地页仓库",
    importance: 0.6, confidence: 1, dataSource: "registry",
    properties: { format: "repo", path: "78tyih/htx-otc-landing" },
    relations: [R("asset.htx-otc-landing", "part_of", "project.htx-otc", 1)],
  }),
  make("asset.propfirm-tv-factory", {
    type: "Asset", name: "PropFirm.TV Video Factory", description: "视频工厂仓库",
    importance: 0.6, confidence: 1, dataSource: "registry",
    properties: { format: "repo", path: "78tyih/propfirm-tv-video-factory" },
    relations: [R("asset.propfirm-tv-factory", "part_of", "project.propfirm-tv", 1)],
  }),
  make("asset.tradespan-logo", {
    type: "Asset", name: "TradeSpan Logo", description: "品牌 Logo",
    importance: 0.5, confidence: 1, dataSource: "spec",
    properties: { format: "SVG", path: "assets/logo.svg" },
    relations: [R("asset.tradespan-logo", "part_of", "project.tradespan", 1)],
  }),
  make("asset.htx-design-refer", {
    type: "Asset", name: "HTX Design Reference", description: "HTX 设计参照库",
    importance: 0.5, confidence: 1, dataSource: "registry",
    properties: { format: "repo", path: "78tyih/htx-design-refer" },
    relations: [R("asset.htx-design-refer", "part_of", "project.sera-agent-console", 0.8)],
  }),
]

// ---------- Tasks（真实项目 + spec 示例 派生） ----------

const tasks: SMOPObject[] = [
  make("task.propfirm-tv.video-production", {
    type: "Task", name: "PropFirm 视频生产", description: "口播 → 脚本 → 素材 → 合成 → 发布",
    status: "active", importance: 0.8, confidence: 1, dataSource: "spec",
    properties: { priority: "high", summary: "PropFirm 视频生产（口播→合成→发布）", status: "in_progress" },
    relations: [
      R("task.propfirm-tv.video-production", "part_of", "project.propfirm-tv", 1),
      R("task.propfirm-tv.video-production", "assigned_to", "agent.video", 1),
      R("task.propfirm-tv.video-production", "follows_rule", "rule.financial.trust-first", 0.9),
      R("task.propfirm-tv.video-production", "follows_decision", "decision.video.react-gsap", 0.8),
    ],
  }),
  make("task.tradespan.landing-page", {
    type: "Task", name: "构建 TradeSpan 落地页", description: "根据设计决策构建官网着陆页",
    status: "active", importance: 0.75, confidence: 1, dataSource: "spec",
    properties: { priority: "high", summary: "TradeSpan 官网落地页", status: "in_progress", deadline: "2026-08-25" },
    relations: [
      R("task.tradespan.landing-page", "part_of", "project.tradespan", 1),
      R("task.tradespan.landing-page", "assigned_to", "agent.design", 1),
      R("task.tradespan.landing-page", "follows_decision", "decision.tradespan.dark-ui", 0.9),
      R("task.tradespan.landing-page", "follows_rule", "rule.financial.trust-first", 0.8),
    ],
  }),
  make("task.htx-otc.landing-page", {
    type: "Task", name: "HTX OTC 落地页与进度中心", description: "暗色金融风落地页",
    status: "active", importance: 0.75, confidence: 1, dataSource: "spec",
    properties: { priority: "high", summary: "HTX OTC 落地页与进度中心", status: "in_progress" },
    relations: [
      R("task.htx-otc.landing-page", "part_of", "project.htx-otc", 1),
      R("task.htx-otc.landing-page", "assigned_to", "agent.design", 1),
      R("task.htx-otc.landing-page", "follows_decision", "decision.htx-otc.dark-financial", 0.9),
      R("task.htx-otc.landing-page", "follows_rule", "rule.financial.trust-first", 0.8),
    ],
  }),
  make("task.sera-console.context-runtime", {
    type: "Task", name: "Sera 控制中心 · Context Runtime 页", description: "把 SMOP Context Package 编译算法落到真实数据",
    status: "active", importance: 0.85, confidence: 1, dataSource: "spec",
    properties: { priority: "critical", summary: "Context Runtime：真实数据桥 → Context Package", status: "in_progress" },
    relations: [
      R("task.sera-console.context-runtime", "part_of", "project.sera-agent-console", 1),
      R("task.sera-console.context-runtime", "assigned_to", "agent.ceo", 1),
      R("task.sera-console.context-runtime", "follows_decision", "decision.design.htx-brand", 0.9),
      R("task.sera-console.context-runtime", "follows_rule", "rule.org.system-over-individual", 0.8),
    ],
  }),
  make("task.deltapex.site", {
    type: "Task", name: "Deltapex 官网与品牌", description: "德湃考试盘官网、品牌、满意度调研",
    status: "active", importance: 0.7, confidence: 1, dataSource: "spec",
    properties: { priority: "high", summary: "Deltapex 官网与品牌建设", status: "in_progress" },
    relations: [
      R("task.deltapex.site", "part_of", "project.deltapex", 1),
      R("task.deltapex.site", "assigned_to", "agent.propfirm", 1),
      R("task.deltapex.site", "follows_rule", "rule.financial.trust-first", 0.8),
    ],
  }),
  make("task.traderbti.analysis", {
    type: "Task", name: "Trader BTI 市场分析", description: "交易平台市场研究与竞品分析",
    status: "active", importance: 0.6, confidence: 1, dataSource: "spec",
    properties: { priority: "medium", summary: "Trader BTI 市场分析", status: "in_progress" },
    relations: [
      R("task.traderbti.analysis", "part_of", "project.traderbti", 1),
      R("task.traderbti.analysis", "assigned_to", "agent.trading", 1),
    ],
  }),
]

// ---------- 汇总 store ----------

const all: SMOPObject[] = [
  personSera,
  companySera,
  ...agents,
  ...projects,
  ...skills,
  ...workflows,
  ...decisions,
  ...experiences,
  ...rules,
  ...assets,
  ...tasks,
]

export function getAllObjects(): SMOPObject[] {
  return all
}

export function getObject(id: string): SMOPObject | undefined {
  return all.find(o => o.id === id)
}

export function getObjectsByType(type: ObjectType): SMOPObject[] {
  return all.filter(o => o.type === type)
}

export const DATA_SOURCE_LABEL: Record<DataSource, string> = {
  registry: "真实注册表",
  "agent-yaml": "员工契约",
  constitution: "公司宪法",
  spec: "规范态数据",
}