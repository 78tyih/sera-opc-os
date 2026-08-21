// UI 翻译字典
const dict: Record<string, { zh: string; en: string }> = {
  // Navigation
  "nav.dashboard": { zh: "控制台", en: "Dashboard" },
  "nav.canvas": { zh: "画布", en: "Canvas" },
  "nav.projects": { zh: "项目", en: "Projects" },
  "nav.agents": { zh: "智能体", en: "Agents" },
  "nav.workflows": { zh: "工作流", en: "Workflows" },
  "nav.department": { zh: "组织", en: "Department" },
  "nav.console": { zh: "内核", en: "Console" },
  "nav.all-operational": { zh: "系统正常", en: "All operational" },
  "nav.search": { zh: "搜索...", en: "Search..." },

  // Dashboard
  "dashboard.title": { zh: "控制台", en: "Dashboard" },
  "dashboard.subtitle": { zh: "控制中心概览", en: "Control Center" },
  "dashboard.active-projects": { zh: "活跃项目", en: "Active Projects" },
  "dashboard.running-agents": { zh: "运行中", en: "Running" },
  "dashboard.today-output": { zh: "今日产出", en: "Today" },
  "dashboard.system-uptime": { zh: "系统运行", en: "Uptime" },
  "dashboard.active-agents": { zh: "活跃智能体", en: "Active Agents" },
  "dashboard.running-workflows": { zh: "运行中工作流", en: "Running Workflows" },
  "dashboard.activity": { zh: "动态", en: "Activity" },
  "dashboard.view-all": { zh: "查看全部", en: "View all" },

  // Projects
  "projects.title": { zh: "项目", en: "Projects" },
  "projects.new": { zh: "新建项目", en: "New Project" },
  "projects.no-match": { zh: "暂无匹配项目", en: "No matching projects" },

  // Agents
  "agents.title": { zh: "智能体", en: "Agents" },
  "agents.subtitle": { zh: "部门化 AI 团队", en: "Departmental Agent Team" },
  "agents.active": { zh: "活跃", en: "Active" },
  "agents.idle": { zh: "闲置", en: "Idle" },

  // Workflows
  "workflows.title": { zh: "工作流", en: "Workflows" },
  "workflows.subtitle": { zh: "工作流编排", en: "Workflow Orchestration" },
  "workflows.run": { zh: "运行", en: "Run" },
  "workflows.pause": { zh: "暂停", en: "Pause" },
  "workflows.last-run": { zh: "上次运行", en: "Last run" },
  "workflows.completed": { zh: "已完成", en: "Completed" },
  "workflows.running": { zh: "运行中", en: "Running" },
  "workflows.pending": { zh: "待处理", en: "Pending" },

  // Department
  "department.title": { zh: "组织架构", en: "Department" },
  "department.subtitle": { zh: "组织结构", en: "Organizational Structure" },
  "department.team-members": { zh: "团队成员", en: "Team Members" },
  "department.active-projects": { zh: "活跃项目", en: "Active Projects" },
  "department.ceo": { zh: "首席执行官", en: "CEO" },

  // Status
  "status.active": { zh: "活跃", en: "Active" },
  "status.idle": { zh: "闲置", en: "Idle" },
  "status.running": { zh: "运行中", en: "Running" },
  "status.pending": { zh: "待处理", en: "Pending" },
  "status.completed": { zh: "已完成", en: "Completed" },
  "status.planning": { zh: "规划中", en: "Planning" },
  "status.high": { zh: "高", en: "High" },
  "status.medium": { zh: "中", en: "Medium" },
  "status.critical": { zh: "紧急", en: "Critical" },

  // Categories
  "cat.all": { zh: "全部", en: "All" },
  "cat.product": { zh: "产品", en: "Product" },
  "cat.content": { zh: "内容", en: "Content" },
  "cat.infrastructure": { zh: "基础设施", en: "Infrastructure" },
  "cat.business": { zh: "商务", en: "Business" },

  // Departments
  "dept.product": { zh: "产品部", en: "Product" },
  "dept.design": { zh: "设计部", en: "Design" },
  "dept.marketing": { zh: "市场部", en: "Marketing" },
  "dept.content": { zh: "内容部", en: "Content" },
  "dept.engineering": { zh: "工程部", en: "Engineering" },
  "dept.business": { zh: "商务部", en: "Business" },

  // Misc
  "misc.agents": { zh: "个智能体", en: " agents" },
  "misc.projects": { zh: "个项目", en: " projects" },
}

// 数据文本翻译字典（英文 → 中文）
const textDict: Record<string, string> = {
  // === Agent Names ===
  "Product Agent": "产品智能体",
  "Brand Agent": "品牌智能体",
  "UI Agent": "UI 智能体",
  "Motion Agent": "动效智能体",
  "SEO Agent": "SEO 智能体",
  "Growth Agent": "增长智能体",
  "Script Agent": "脚本智能体",
  "Video Agent": "视频智能体",
  "Frontend Agent": "前端智能体",
  "Backend Agent": "后端智能体",
  "PropFirm Agent": "PropFirm 智能体",
  "OTC Agent": "OTC 智能体",
  "Trading Agent": "交易智能体",

  // === Agent Roles ===
  "Product Strategy & Roadmap": "产品策略与路线图",
  "Brand Identity & Strategy": "品牌识别与策略",
  "User Interface Design": "用户界面设计",
  "Animation & Interaction": "动效与交互设计",
  "Search Engine Optimization": "搜索引擎优化",
  "Growth Marketing": "增长营销",
  "Content Script Writing": "内容脚本撰写",
  "Video Production & Editing": "视频制作与编辑",
  "Frontend Development": "前端开发",
  "Backend Development": "后端开发",
  "PropFirm Industry Intelligence": "PropFirm 行业情报",
  "OTC Trading & Client Management": "OTC 交易与客户管理",
  "Trading Research & Analysis": "交易研究与分析",

  // === Agent Skills ===
  "Market Research": "市场调研",
  "PRD Writing": "PRD 撰写",
  "User Story Mapping": "用户故事地图",
  "A/B Testing": "A/B 测试",
  "Brand Strategy": "品牌策略",
  "Visual Identity": "视觉识别",
  "Design System": "设计系统",
  "Copywriting": "文案撰写",
  "UI Design": "UI 设计",
  "Component Library": "组件库",
  "Prototyping": "原型设计",
  "Design Tokens": "设计令牌",
  "Motion Design": "动效设计",
  "Micro-interactions": "微交互",
  "Keyword Research": "关键词研究",
  "Content Strategy": "内容策略",
  "Technical SEO": "技术 SEO",
  "Analytics": "数据分析",
  "Growth Strategy": "增长策略",
  "Campaign Management": "活动管理",
  "Experimentation": "实验设计",
  "Script Writing": "脚本撰写",
  "Storyboarding": "故事板",
  "Voice Direction": "配音指导",
  "Narration": "旁白",
  "Video Editing": "视频剪辑",
  "Motion Graphics": "动态图形",
  "Color Grading": "色彩校正",
  "Compositing": "合成",
  "Competitive Analysis": "竞品分析",
  "Market Intelligence": "市场情报",
  "Browser Automation": "浏览器自动化",
  "Content Factory": "内容工厂",
  "Client Profiling": "客户画像",
  "Risk Assessment": "风险评估",
  "Quote Management": "报价管理",
  "Technical Analysis": "技术分析",
  "Order Flow": "订单流",
  "Backtesting": "回测",

  // === Agent Descriptions ===
  "Defines product vision, prioritizes features, and manages the product lifecycle.": "制定产品愿景，排定功能优先级，管理产品生命周期。",
  "Guardian of brand consistency across all touchpoints.": "守护品牌在所有触点上的一致性。",
  "Crafts pixel-perfect interfaces and maintains the component library.": "打造像素级完美的界面，维护组件库。",
  "Brings interfaces to life with purposeful animation.": "通过有目的的动效让界面生动起来。",
  "Drives organic growth through data-driven SEO strategies.": "通过数据驱动的 SEO 策略推动自然增长。",
  "Experiments and scales growth channels across the funnel.": "实验并规模化增长渠道，覆盖全漏斗。",
  "Writes compelling scripts for video content and presentations.": "为视频内容和演示撰写引人入胜的脚本。",
  "Produces polished video content from raw footage to final delivery.": "从原始素材到最终交付，制作精良的视频内容。",
  "Builds responsive, performant user interfaces with modern frameworks.": "使用现代框架构建响应式、高性能的用户界面。",
  "Designs and implements scalable server-side architecture.": "设计和实现可扩展的服务端架构。",
  "Monitors PropFirm competitors, analyzes products, and generates marketing assets.": "监控 PropFirm 竞品，分析产品，生成营销资产。",
  "Manages OTC client relationships, quotes, and risk assessment workflows.": "管理 OTC 客户关系、报价和风险评估流程。",
  "Conducts trading research, backtests strategies, and analyzes market structure.": "开展交易研究，回测策略，分析市场结构。",

  // === Department Descriptions ===
  "Defines product vision, strategy, and roadmap.": "定义产品愿景、策略和路线图。",
  "Crafts brand identity, UI, and motion experiences.": "打造品牌识别、UI 和动效体验。",
  "Drives growth through SEO, campaigns, and analytics.": "通过 SEO、活动和数据分析驱动增长。",
  "Creates compelling scripts and video content.": "创作引人入胜的脚本和视频内容。",
  "Builds and maintains the technical infrastructure.": "构建和维护技术基础设施。",
  "Manages PropFirm intelligence, OTC trading, and market research.": "管理 PropFirm 情报、OTC 交易和市场研究。",

  // === Project Descriptions ===
  "Daily PropFirm intelligence video production pipeline": "每日 PropFirm 情报视频制作流水线",
  "AI-powered education platform for children": "AI 驱动的儿童教育平台",
  "MT4/MT5 trading software product launch": "MT4/MT5 交易软件产品发布",
  "Personal AI Operating System — cross-platform agent orchestration": "个人 AI 操作系统 — 跨平台智能体编排",
  "Automated content generation and asset management pipeline": "自动化内容生成与资产管理流水线",
  "OTC customer relationship management system": "OTC 客户关系管理系统",

  // === Workflow Names ===
  "Product Launch Pipeline": "产品发布管道",
  "Daily Intelligence Brief": "每日情报简报",
  "Video Production Pipeline": "视频制作管道",

  // === Workflow Descriptions ===
  "End-to-end product launch workflow from research to distribution": "从调研到分发的全流程产品发布工作流",
  "Automated competitor monitoring and intelligence report generation": "自动竞品监控与情报报告生成",
  "From script to published video asset": "从脚本到发布视频资产的全流程",

  // === Workflow Node Labels ===
  "Product Input": "产品输入",
  "Content": "内容",
  "Video": "视频",
  "Positioning": "定位",
  "Brand Design": "品牌设计",
  "Website": "网站",
  "Launch": "发布",
  "Daily Trigger": "每日触发",
  "Scrape Competitors": "抓取竞品",
  "Analyze Intel": "分析情报",
  "Generate Report": "生成报告",
  "Push to WeCom": "推送至企业微信",
  "Script Input": "脚本输入",
  "Storyboard": "故事板",
  "Voiceover": "配音",
  "Render": "渲染",
  "Review": "审核",
  "Archive to Eagle": "归档至 Eagle",

  // === Workflow Node Skills ===
  "Brief": "简报",
  "Strategy": "策略",
  "Landing Page": "落地页",
  "Production": "制作",
  "Distribution": "分发",
  "Cron": "定时任务",
  "Intelligence": "情报",
  "Notification": "通知",
  "Writing": "撰写",
  "Visual Planning": "视觉规划",
  "TTS/Recording": "TTS/录制",
  "Quality Check": "质量检查",
  "Asset Manager": "资产管理",

  // === Agent Names in Workflow Context ===
  "user": "用户",
  "system": "系统",
  "multi": "多智能体",
  "Content Agent": "内容智能体",
  "Design Agent": "设计智能体",
}

export function t(key: string, lang: "zh" | "en"): string {
  return dict[key]?.[lang] ?? key
}

export function tz(key: string): { zh: string; en: string } {
  return dict[key] ?? { zh: key, en: key }
}

// 翻译任意文本（主要用于数据源中的英文文本）
export function translateText(text: string, lang: "zh" | "en"): string {
  if (lang === "en") return text
  return textDict[text] ?? text
}

// 工具名/软件名等专有名词，保持原文
const properNouns = new Set([
  "Linear", "Notion", "Figma", "Adobe Creative Suite", "Brand Guidelines",
  "Storybook", "Tailwind", "After Effects", "Rive", "LottieFiles",
  "Ahrefs", "Google Search Console", "SEMrush", "Mixpanel", "Google Analytics",
  "HubSpot", "Final Draft", "ElevenLabs", "ComfyUI", "Premiere Pro",
  "Eagle", "VS Code", "Chrome DevTools", "Vercel", "Docker", "Postman",
  "DataGrip", "Browser", "WeCom", "Lark", "Mail", "CRM", "ATAS",
  "TradingView", "Jupyter", "React", "Next.js", "TypeScript", "Python",
  "Node.js", "PostgreSQL", "Redis", "Tailwind CSS", "Framer Motion",
  "Lottie", "GSAP", "SEO", "PRD", "OTC", "CRM", "API",
  "PropFirm TV", "Niuniu AI", "TradeSpan", "Sera OPC OS", "Content Factory",
  "OTC CRM",
])

export function isProperNoun(text: string): boolean {
  return properNouns.has(text)
}