# Sera Memory Engine V1 技术架构

> **⚠️ 已废弃 — 仅供参考**
>
> 本文档已被 [Sera Context Runtime & Learning OS V1.1](Sera-Context-Runtime-Learning-OS-V1.md) 取代。
> 关键差异：ID 命名从下划线（`project_tradespan_001`）改为点分（`project.tradespan`），
> 存储方案从纯 SQLite 改为 Memory Matrix，新增 Context Governor / Learning Engine 等机制。
> **所有新实现请以 canonical 文档为准，勿参考本文件。**

## AI 公司的大脑基础设施

| Field | Value |
|-------|-------|
| Version | 1.0 (Deprecated) |
| Status | Superseded — 参考 canonical |
| Owner | Sera CTO |
| Layer | Foundation (Layer 0) |
| Predecessor | Sera Memory Graph Schema V1 |
| Target | DeepSeek / Trae / Codex Direct Execution |

---

# 0. Executive Summary

## 问题

Sera OPCOS 有 12 类 Entity、多种 Relation、三层 Memory。如果没有 Engine，这些只是 Schema 文件。

## 解决方案

Sera Memory Engine 是一个**多模态存储 + 自动提取 + 语义检索 + 记忆构建**的引擎。

它让所有 Agent 可以：

```
查询 → 不是搜文件，而是问"公司知道什么"
存储 → 不是写文件，而是"记录一次经验"
推理 → 不是遍历目录，而是"沿着关系图走"
学习 → 不是读日志，而是"接收每日组织记忆"
```

## 核心设计原则

1. **本地优先** — 所有数据存储在本地，不依赖云服务
2. **多模态** — 同时支持向量、图、全文检索
3. **零配置** — clone 即用，不需要运维数据库
4. **渐进式** — 从单文件 JSON 起步，可平滑升级到分布式
5. **Agent 原生** — API 设计面向 AI 读取，而非人类阅读

---

# 一、整体架构

```
┌─────────────────────────────────────────────────────────┐
│                     Agent API Layer                      │
│  /memory/query  /memory/store  /memory/relate  /memory/search │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    Orchestrator Layer                    │
│   Query Planner  │  Result Fusion  │  Cache Manager     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Indexing Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐      │
│  │  Vector   │  │  Graph   │  │  Keyword (FTS5)  │      │
│  │  Search   │  │  Traverse│  │  Search          │      │
│  └──────────┘  └──────────┘  └──────────────────┘      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    Storage Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐      │
│  │  SQLite  │  │  LanceDB │  │  Filesystem      │      │
│  │(Entities │  │(Vectors) │  │(Assets/BLOBs)    │      │
│  │ Relations│  │          │  │                  │      │
│  │ Metadata)│  │          │  │                  │      │
│  └──────────┘  └──────────┘  └──────────────────┘      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Extractor Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Markdown│  │  GitHub  │  │  Chat    │  │  Email  │ │
│  │  Parser  │  │  Parser  │  │  Parser  │  │  Parser │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

# 二、存储层设计

## 2.1 存储选型决策矩阵

| 维度 | SQLite | PostgreSQL | Neo4j | LanceDB | Chroma |
|------|--------|------------|-------|---------|--------|
| 部署复杂度 | ★★★★★ | ★★ | ★★ | ★★★★★ | ★★★★ |
| 图查询能力 | ★★★ | ★★★ | ★★★★★ | ★ | ★ |
| 向量搜索 | ★ | ★★★ | ★★ | ★★★★★ | ★★★★ |
| 全文检索 | ★★★★★ | ★★★★ | ★ | ★ | ★ |
| 零配置运行 | ★★★★★ | ★ | ★ | ★★★★★ | ★★★★ |
| 分布式扩展 | ★ | ★★★★★ | ★★★★★ | ★★★ | ★★ |
| 生态成熟度 | ★★★★★ | ★★★★★ | ★★★★ | ★★★ | ★★★ |

## 2.2 推荐方案：Hybrid Tri-Store

V1 版本采用**三层存储**，各自发挥最强能力：

### 存储层 A: SQLite（主存储）

**角色：** Entity 存储、Relation 管理、Metadata、全文检索

**理由：**
- 零配置，单文件，clone 即用
- 支持 FTS5 全文索引
- 支持递归 CTE 做图遍历
- Mac 原生支持，Serwin 电脑直接使用
- Turso 提供分布式扩展路径

**核心表结构：**

```sql
-- ============================================
-- Entity 表
-- ============================================
CREATE TABLE entities (
    id          TEXT PRIMARY KEY,          -- e.g. "project_tradespan_001"
    type        TEXT NOT NULL,             -- Person | Company | Project | Product | Agent | Skill | Workflow | Asset | Decision | Experience | Conversation | Event
    name        TEXT NOT NULL,
    state       TEXT DEFAULT 'active',     -- active | archived | deprecated
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

-- ============================================
-- Attributes 表（JSON 扩展）
-- ============================================
CREATE TABLE attributes (
    entity_id   TEXT NOT NULL REFERENCES entities(id),
    key         TEXT NOT NULL,
    value_json  TEXT NOT NULL,            -- JSON 格式，支持任意结构
    PRIMARY KEY (entity_id, key)
);

-- ============================================
-- Relations 表（图的核心）
-- ============================================
CREATE TABLE relations (
    id              TEXT PRIMARY KEY,
    source_id       TEXT NOT NULL REFERENCES entities(id),
    target_id       TEXT NOT NULL REFERENCES entities(id),
    relation_type   TEXT NOT NULL,        -- owns | manages | depends_on | creates | implements | learned_from | related_to
    weight          REAL DEFAULT 1.0,     -- 关系强度 0.0 ~ 1.0
    metadata_json   TEXT,                 -- 额外的上下文
    created_at      TEXT NOT NULL,
    UNIQUE(source_id, target_id, relation_type)
);

CREATE INDEX idx_relations_source ON relations(source_id);
CREATE INDEX idx_relations_target ON relations(target_id);
CREATE INDEX idx_relations_type ON relations(relation_type);

-- ============================================
-- Memory 表
-- ============================================
CREATE TABLE memories (
    id          TEXT PRIMARY KEY,
    entity_id   TEXT NOT NULL REFERENCES entities(id),
    level       TEXT NOT NULL,            -- short_term | project | organizational
    content     TEXT NOT NULL,
    source      TEXT,                     -- 来源：obsidian | github | chat | email | manual
    importance  REAL DEFAULT 0.5,         -- 重要性 0.0 ~ 1.0
    created_at  TEXT NOT NULL,
    expires_at  TEXT                      -- short_term 过期时间，NULL 表示永不过期
);

CREATE INDEX idx_memories_entity ON memories(entity_id);
CREATE INDEX idx_memories_level ON memories(level);

-- ============================================
-- 全文搜索（FTS5）
-- ============================================
CREATE VIRTUAL TABLE entities_fts USING fts5(
    name,
    content,       -- 从 attributes 和 memories 聚合的文本
    entity_id UNINDEXED
);

-- ============================================
-- History 表（追踪所有变更）
-- ============================================
CREATE TABLE history (
    id          TEXT PRIMARY KEY,
    entity_id   TEXT NOT NULL REFERENCES entities(id),
    action      TEXT NOT NULL,            -- created | updated | deleted | related
    snapshot    TEXT NOT NULL,            -- 变更后的 JSON 快照
    timestamp   TEXT NOT NULL
);

CREATE INDEX idx_history_entity ON history(entity_id);
CREATE INDEX idx_history_timestamp ON history(timestamp);
```

### 存储层 B: LanceDB（向量存储）

**角色：** 语义搜索、相似度匹配、经验检索

**理由：**
- 嵌入式向量数据库，无需独立服务
- 支持本地文件存储
- 支持多模态向量（文本、代码）
- 与 SQLite 互补，SQLite 管精确查询，LanceDB 管模糊语义

**数据结构：**

```
memory_vectors/
├── lance/                    # LanceDB 底层存储
│   ├── _versions/
│   ├── transactions.lance
│   └── data.lance
└── schema.json               # 向量映射配置

向量表结构：
┌──────────────┬──────────────┬──────────────┬──────────────┐
│  entity_id   │  vector      │  chunk_text  │  metadata    │
│  (TEXT)      │  (FLOAT32[]) │  (TEXT)      │  (JSON)      │
├──────────────┼──────────────┼──────────────┼──────────────┤
│  project_001 │  [0.1, ...]  │  "TradeSpan" │  {type:...}  │
│  decision_02 │  [-0.3, ...] │  "Dark UI"   │  {type:...}  │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**向量化配置：**

```yaml
# memory-vector-config.yaml
embedding_model: "text-embedding-3-small"   # OpenAI
fallback_model: "all-MiniLM-L6-v2"         # 本地离线
dimension: 1536
chunk_size: 512
chunk_overlap: 64
index_type: "IVF_PQ"                       # 索引类型
metric: "cosine"
```

### 存储层 C: Filesystem（资产存储）

**角色：** 大文件、图片、视频、二进制资产

**路径约定：**

```
memory/
├── sqlite/
│   └── sera-memory.db                     # SQLite 主数据库
├── vectors/
│   └── lance/                             # LanceDB 向量存储
├── assets/
│   ├── images/
│   ├── videos/
│   ├── documents/
│   └── raw/                              # 未处理的原始文件
├── archive/
│   └── daily-memory/                     # 每日组织记忆归档
└── config/
    ├── memory-config.yaml
    └── extractor-config.yaml
```

---

# 三、索引层设计

## 3.1 三种检索路径

### 路径 A: 精确查询（SQLite）

用于已知 ID、类型、名称的精确匹配。

```
GET /memory/query
{
  "exact": {
    "id": "project_tradespan_001",
    "type": "Project"
  }
}

→ SQL:
  SELECT * FROM entities
  WHERE id = 'project_tradespan_001'
  AND type = 'Project'
```

### 路径 B: 语义搜索（LanceDB）

用于自然语言查询，不知道精确名称。

```
GET /memory/search
{
  "query": "TradeSpan 项目的设计决策是什么",
  "type": "Decision",
  "top_k": 5
}

→ Pipeline:
  1. 向量化 query → [0.1, -0.3, ...]
  2. LanceDB 搜索相似向量
  3. 返回匹配的 entity_id
  4. SQLite 补充完整信息
```

### 路径 C: 图遍历（SQLite CTE）

用于关系推理，沿着关系图走。

```
GET /memory/traverse
{
  "start_id": "person_sera_001",
  "relation": "owns",
  "depth": 2
}

→ SQL:
  WITH RECURSIVE traverse AS (
    SELECT source_id, target_id, relation_type, 1 AS depth
    FROM relations
    WHERE source_id = 'person_sera_001'
    AND relation_type = 'owns'
    UNION ALL
    SELECT r.source_id, r.target_id, r.relation_type, t.depth + 1
    FROM relations r
    JOIN traverse t ON r.source_id = t.target_id
    WHERE t.depth < 2
  )
  SELECT * FROM traverse;
```

## 3.2 混合搜索（Hybrid Search）

Agent 最常见需求：**自然语言 + 类型过滤 + 关系约束**

```
GET /memory/hybrid
{
  "query": "failed video projects",
  "type": "Experience",
  "relation_filter": {
    "source": "project_tradespan_001",
    "relation": "related_to"
  },
  "top_k": 10,
  "fusion": "rrf"           # Reciprocal Rank Fusion
}

→ Pipeline:
  1. Vector Search → rank A
  2. SQLite exact match → rank B
  3. FTS5 keyword match → rank C
  4. Graph traversal → filter D
  5. RRF fusion → final result
```

## 3.3 缓存策略

```
Cache Layer (In-Memory LRU)
├── hot_entities:   最近访问的 Entity（TTL: 5min）
├── query_cache:    重复查询结果（TTL: 1min）
├── vector_cache:   最近向量化结果（TTL: 10min）
└── graph_cache:    常用子图（TTL: 30min）
```

---

# 四、Extractor 设计

## 4.1 整体架构

```
Extractor Pipeline
│
├── 1. Connector
│   ├── Obsidian Connector   → 监控 Markdown 文件变更
│   ├── GitHub Connector     → Webhook / Polling
│   ├── Chat Connector       → Trae / ChatGPT API
│   └── Email Connector      → IMAP
│
├── 2. Parser
│   ├── Markdown Parser      → Frontmatter + Content
│   ├── Code Parser          → Commit message + Diff
│   ├── Conversation Parser  → Thread + Summary
│   └── Email Parser         → Subject + Body + Attachments
│
├── 3. Entity Recognizer
│   ├── Rule-based           → 正则匹配已知模式
│   ├── LLM-based            → 调用 LLM 提取实体
│   └── Hybrid               → 规则优先 + LLM 兜底
│
└── 4. Graph Writer
    ├── Entity Writer         → INSERT/UPDATE entities
    ├── Relation Writer       → INSERT relations
    ├── Memory Writer         → INSERT memories
    └── Vector Indexer        → LanceDB upsert
```

## 4.2 Obsidian Markdown Extractor

这是最核心的提取器，因为 Obsidian 是用户的主知识库。

**提取规则：**

```yaml
# extractor-rules.yaml
obsidian:
  watch_path: "~/Obsidian/"

  # 文件路径 → Entity 类型映射
  path_mapping:
    "02_Project/": "Project"
    "03_Product/": "Product"
    "04_Area/": "Skill"
    "05_Archive/": "Experience"
    "06_Daily/": "Event"

  # Frontmatter 字段映射
  frontmatter:
    id: "entity.id"
    type: "entity.type"
    name: "entity.name"
    state: "entity.state"
    tags: "entity.tags"
    related: "relations"
    decision: "entity.decision"

  # 内容提取规则
  content_rules:
    - pattern: "## 决策"           # 标题匹配
      action: extract_decision
    - pattern: "## 经验"           # 标题匹配
      action: extract_experience
    - pattern: "## 技术栈"         # 标题匹配
      action: extract_skill
    - pattern: "[[Link]]"         # Wiki 链接
      action: extract_relation

  # LLM 提取（当规则匹配不到时）
  llm_fallback: true
  llm_prompt: |
    从以下 Markdown 内容中提取实体和关系。
    实体类型：Person, Project, Product, Skill, Decision, Experience
    输出 JSON 格式。

LLM 提取指令模板：

```yaml
# prompts/entity-extraction.yaml
system_prompt: |
  你是一个实体提取器。从文本中识别 Sera Memory Graph Entity。
  实体类型：
  - Person: 人类
  - Project: 项目
  - Product: 产品
  - Skill: 技能
  - Decision: 决策
  - Experience: 经验
  - Event: 事件

  输出格式：
  {
    "entities": [
      {
        "type": "Project",
        "name": "TradeSpan",
        "attributes": {
          "goal": "...",
          "status": "..."
        }
      }
    ],
    "relations": [
      {
        "source": "TradeSpan",
        "target": "React",
        "type": "depends_on"
      }
    ],
    "memories": [
      {
        "level": "project",
        "content": "..."
      }
    ]
  }
```

## 4.3 GitHub Extractor

**连接方式：**

```
GitHub Extractor
│
├── Mode A: Webhook
│   └── 服务器接收 push event
│       ├── commits → 提取变更
│       └── PR merge → 提取决策
│
├── Mode B: CLI Polling
│   └── sera-memory sync --source github
│       ├── git log --oneline
│       └── 读取 commit message
│
└── Mode C: Manual
    └── sera-memory import --file CHANGELOG.md
```

**提取规则：**

```yaml
github:
  commit_rules:
    - pattern: "^feat\\((.+?)\\):"       # feat(TradeSpan):
      action: update_project_feature
    - pattern: "^fix\\((.+?)\\):"        # fix(API):
      action: record_experience
    - pattern: "BREAKING CHANGE"         # break change
      action: record_decision
```

## 4.4 Chat Extractor

**连接方式：**

```
Chat Extractor
│
├── Trae:  读取 conversation session 文件
├── ChatGPT: 导出 JSON 对话
├── Claude: 读取 project knowledge
└── Slack:  API 读取 threads
```

**提取规则：**

```yaml
chat:
  extraction_rules:
    - trigger: "决策："
      action: extract_decision
    - trigger: "经验："
      action: extract_experience
    - trigger: "创建项目"
      action: extract_project
    - trigger: "技能"
      action: extract_skill

  summarization:
    enabled: true
    schedule: "daily"
    prompt: |
      从以下对话中提取关键信息：
      1. 做出的决策
      2. 获得的经验
      3. 创建或修改的项目
      4. 定义的新技能或工作流
```

## 4.5 提取流水线执行流程

```
Input: 任意源文件
│
▼
Step 1: 文件类型识别
  ├── .md → Markdown Parser
  ├── .py / .ts / .js → Code Parser
  ├── .json → Chat Export Parser
  └── .eml → Email Parser
│
▼
Step 2: 原始内容解析
  ├── 提取 frontmatter / metadata
  ├── 提取正文
  └── 提取链接 / 引用
│
▼
Step 3: 实体识别
  ├── 规则匹配（快速）
  ├── 如果有明确 Type → 直接创建
  └── 否则 → LLM 识别（慢但准确）
│
▼
Step 4: 去重合并
  ├── 检查 name + type 是否已存在
  ├── 如果存在 → 更新 attributes
  └── 如果不存在 → 创建新 entity
│
▼
Step 5: 关系提取
  ├── Wiki 链接 → related_to
  ├── Frontmatter related → 指定关系
  └── LLM 识别 → 最佳匹配关系
│
▼
Step 6: 存储
  ├── entities → SQLite
  ├── relations → SQLite
  ├── memories → SQLite + LanceDB
  └── assets → Filesystem
```

---

# 五、Memory Builder 设计

## 5.1 什么是 Memory Builder

每天自动运行的进程，负责：

```
Input: 当天所有新增数据
  │
  ▼
  1. Consolidate  → 合并去重
  2. Summarize    → 生成摘要
  3. Analyze      → 提取模式
  4. Rank         → 评估重要性
  5. Build        → 生成每日组织记忆
  │
  ▼
Output: Daily Organizational Memory Artifact
```

## 5.2 构建流程

```yaml
# memory-builder-config.yaml
schedule:
  daily: "23:00"                    # 每天晚 11 点运行
  weekly: "fri 18:00"              # 每周五下午 6 点
  cleanup: "sun 03:00"             # 每周日清理短期记忆

pipeline:
  # Step 1: 收集当天数据
  - stage: collect
    sources:
      - obsidian_changes
      - github_commits
      - chat_extractions
      - email_extractions

  # Step 2: 实体合并去重
  - stage: deduplicate
    threshold: 0.85                # 余弦相似度 > 0.85 视为同一实体
    strategy: merge_attributes     # 合并属性，保留最新

  # Step 3: 自动建立关系
  - stage: auto_relate
    rules:
      - "同一 Project 下的所有 Entity 自动 related_to"
      - "同一 Conversation 中提到的 Entity 自动 related_to"
      - "Experience 中失败的 Task 关联到其 Project"

  # Step 4: 重要性评分
  - stage: rank_importance
    factors:
      - access_frequency: 0.3      # 被访问频率
      - relation_count: 0.2        # 关系数量
      - recency: 0.3               # 最近活跃度
      - user_defined: 0.2         # 用户手动标记

  # Step 5: 生成摘要
  - stage: summarize
    max_tokens: 2048
    template: |
      # 每日组织记忆 - {date}

      ## 活跃项目
      {active_projects}

      ## 新决策
      {new_decisions}

      ## 关键经验
      {key_experiences}

      ## 新增技能
      {new_skills}

      ## 待办事项
      {action_items}

      ## 趋势分析
      {trends}

  # Step 6: 短期记忆过期
  - stage: expire
    short_term_ttl: 48            # 48 小时后过期
    archive: true                  # 过期前归档到 SQLite history
```

## 5.3 每日组织记忆输出示例

```markdown
# 每日组织记忆 - 2026-08-21

## 活跃项目
| 项目 | 状态 | 今日变更 |
|------|------|---------|
| TradeSpan | Active | 新增 MT5 连接器 |
| PropFirm TV | Building | 完成 3 个视频脚本 |

## 新决策
1. **TradeSpan UI 风格** — 采用暗色金融科技风格
   - 决策者：Sera
   - 原因：增强信任感
   - 关系：影响 Website, Video Asset

2. **视频生成流程** — 从纯 AI 视频切换到 React Motion
   - 决策者：Sera
   - 原因：纯 AI 视频缺乏 UI 控制感
   - 来源：Experience #exp_003 (失败经验)

## 关键经验
1. **纯 AI 视频的局限性** (重要性: 0.9)
   - 问题：AI 生成的视频无法精确控制 UI 元素
   - 解决：改用 React + GSAP 生成前端动效
   - 状态：已沉淀为 Skill #VideoFactoryV2

## 新增技能
| 名称 | 类别 | 状态 |
|------|------|------|
| Video Factory V2 | Video | Ready |
| MT5 Connector | Integration | Developing |

## 待办事项
1. 完成 Video Factory V2 文档
2. 测试 MT5 连接器

## 趋势分析
- 视频生产周期从 4 小时缩短到 1.5 小时
- Skill 复用率 75%
- 本周决策质量评分 8.5/10
```

## 5.4 Memory 生命周期管理

```
                          Time
                          │
Short-Term Memory         │  hours/days
(current task context)    │  自动过期/归档
                          │
                          ▼
                          │
Project Memory            │  weeks/months
(project context)         │  手动归档
                          │
                          ▼
                          │
Organizational Memory     │  permanent
(company knowledge)       │  持续积累
                          │
                          ▼
                          │
Memory Evolution          │
(跨项目模式识别)           │  AI 自动发现
                          │
                          ▼
```

---

# 六、Agent API 协议

## 6.1 API 设计原则

1. **Agent 是消费者** — API 设计面向 AI 读取，返回结构化数据
2. **一次查询，完整信息** — 不需要 Agent 多次调用拼凑
3. **自然语言优先** — 支持语义查询，不需要精确 ID
4. **关系自动展开** — 返回 Entity 时附带其关系网络

## 6.2 API 端点

### POST /memory/query

精确查询 Entity。

```json
// Request
{
  "id": "project_tradespan_001"
}

// 或
{
  "type": "Project",
  "name": "TradeSpan"
}

// Response
{
  "entity": {
    "id": "project_tradespan_001",
    "type": "Project",
    "name": "TradeSpan",
    "state": "active",
    "attributes": {
      "goal": "连接 ATAS 和 MT4",
      "department": "Engineering"
    },
    "relations": [
      {"type": "belongs_to", "target": {"id": "company_001", "name": "Sera Company"}},
      {"type": "managed_by", "target": {"id": "agent_003", "name": "Product Agent"}},
      {"type": "created_assets", "target": {"id": "asset_001", "name": "Website"}}
    ],
    "memories": [
      {"level": "project", "content": "Brand decision: Dark fintech style", "importance": 0.9}
    ]
  }
}
```

### POST /memory/search

语义搜索。

```json
// Request
{
  "query": "有哪些视频相关的经验教训",
  "type": "Experience",
  "top_k": 5
}

// Response
{
  "results": [
    {
      "entity": {
        "id": "experience_003",
        "type": "Experience",
        "name": "AI 视频缺乏 UI 控制",
        "attributes": {
          "task": "Generate financial video",
          "result": "Failed",
          "reason": "Pure AI video lacked UI",
          "learning": "Need React motion graphics",
          "reusable": "Video Factory V2"
        }
      },
      "score": 0.92,
      "relations": [
        {"type": "related_to", "target": {"name": "Video Factory"}}
      ]
    }
  ]
}
```

### POST /memory/traverse

图遍历。

```json
// Request
{
  "start_id": "person_sera_001",
  "relation": "owns",
  "depth": 2,
  "include_attributes": true
}

// Response
{
  "graph": {
    "nodes": [
      {"id": "person_sera_001", "type": "Person", "name": "Sera"},
      {"id": "company_001", "type": "Company", "name": "Sera Company"},
      {"id": "project_001", "type": "Project", "name": "TradeSpan"},
      {"id": "project_002", "type": "Project", "name": "PropFirm TV"}
    ],
    "edges": [
      {"source": "person_sera_001", "target": "company_001", "type": "owns"},
      {"source": "company_001", "target": "project_001", "type": "owns"},
      {"source": "company_001", "target": "project_002", "type": "owns"}
    ]
  }
}
```

### POST /memory/store

存储新 Entity。

```json
// Request
{
  "entity": {
    "type": "Experience",
    "name": "MT5 连接器延迟问题",
    "attributes": {
      "task": "连接 MT5 到 TradeSpan",
      "result": "延迟过高",
      "reason": "API 轮询间隔不合理",
      "learning": "使用 WebSocket 替代 HTTP 轮询",
      "reusable": "TradeSpan MT5 Module"
    }
  },
  "relations": [
    {"type": "related_to", "target_id": "project_tradespan_001"}
  ]
}

// Response
{
  "id": "experience_004",
  "status": "created",
  "relations_created": 1
}
```

### POST /memory/relate

建立关系。

```json
// Request
{
  "source_id": "experience_004",
  "target_id": "skill_mt5_001",
  "relation_type": "learned_from",
  "metadata": {
    "context": "从 MT5 集成失败中学习到 WebSocket 技能"
  }
}

// Response
{
  "status": "created",
  "relation_id": "relation_042"
}
```

### POST /memory/hybrid

混合搜索（最常用，建议 Agent 优先使用）。

```json
// Request
{
  "query": "TradeSpan 的设计决策和失败经验",
  "filters": {
    "types": ["Decision", "Experience"],
    "related_to": "project_tradespan_001"
  },
  "top_k": 10
}

// Response
{
  "fusion_method": "rrf",
  "results": [
    {
      "entity": {"id": "decision_001", "type": "Decision", "name": "Dark UI 风格"},
      "score": 0.95,
      "matched_by": ["vector", "keyword"]
    },
    {
      "entity": {"id": "experience_003", "type": "Experience", "name": "AI 视频缺乏 UI"},
      "score": 0.88,
      "matched_by": ["vector"]
    }
  ]
}
```

## 6.3 Agent 使用示例

场景：Frontend Agent 被分配做 TradeSpan 页面。

```javascript
// Agent 启动时的查询
const context = await fetch('/memory/hybrid', {
  method: 'POST',
  body: JSON.stringify({
    query: "TradeSpan 项目完整上下文",
    filters: {
      types: ["Decision", "Experience", "Skill", "Asset"],
      related_to: "project_tradespan_001"
    },
    top_k: 20
  })
});

// 返回值（给 Agent 的 prompt 上下文）
`
你正在处理 TradeSpan 项目。

项目背景：
- 目标：连接 ATAS 和 MT4
- 状态：Active

之前的设计决策：
1. 采用暗色金融科技风格（Dark UI）
2. 避免过度动画，强调可信度
3. 左右对齐布局，减少留白

之前的失败经验：
1. 纯 AI 视频缺乏 UI 控制感
   → 改用 React + GSAP 前端动效

可用的技能：
1. Video Factory V2 - 视频生成
2. React Dashboard - 仪表盘组件

已有资产：
1. Logo (SVG)
2. Brand Guidelines (PDF)
3. 参考网站 (Figma)
`
```

---

# 七、CLI 工具设计

## 7.1 命令结构

```bash
sera-memory
├── init                     # 初始化 memory 存储
├── status                   # 查看存储状态
├── query                    # 查询 (JSON 输出)
├── search                   # 语义搜索
├── store                    # 存储实体
├── import                   # 从外部源导入
│   ├── --source obsidian    # 从 Obsidian 导入
│   ├── --source github      # 从 GitHub 导入
│   └── --source chat        # 从聊天记录导入
├── sync                     # 同步所有源
├── build                    # 运行 Memory Builder
├── daily                    # 查看每日组织记忆
├── gc                       # 清理过期短期记忆
├── stats                    # 存储统计信息
└── serve                    # 启动 API 服务
```

## 7.2 使用示例

```bash
# 初始化
sera-memory init --path ~/.sera/memory

# 查看状态
sera-memory status
# → Entities: 47 | Relations: 123 | Memories: 89 | Size: 4.2MB

# 从 Obsidian 导入
sera-memory import --source obsidian --path ~/Obsidian/02_Project/

# 语义搜索
sera-memory search "视频项目失败原因"

# 启动 API 服务（供 Agent 调用）
sera-memory serve --port 8742

# 构建每日记忆
sera-memory build

# 查看每日记忆
sera-memory daily --today
```

---

# 八、技术栈选型总结

| 组件 | 技术选型 | 版本 | 理由 |
|------|---------|------|------|
| **主存储** | SQLite (better-sqlite3) | 3.x | 零配置，单文件，FTS5，CTE |
| **向量存储** | LanceDB | 0.x | 嵌入式，本地优先，多模态 |
| **全文检索** | SQLite FTS5 | 内置 | 无需额外依赖 |
| **Embedding** | text-embedding-3-small | API | 高质量，低成本 |
| **Embedding 离线** | all-MiniLM-L6-v2 | local | 离线兜底 |
| **API 框架** | Express.js / FastAPI | - | 轻量，Agent 友好 |
| **CLI** | Node.js / Python Click | - | 跨平台 |
| **Markdown 解析** | marked / markdown-it | - | 成熟稳定 |
| **Cron** | node-cron / systemd timer | - | 定时构建 |
| **Cache** | Node.js Map / LRU-cache | - | 轻量内存缓存 |

---

# 九、实现路线图

## Phase 1: Foundation（Week 1-2）

```
目标：可运行的存储 + 查询
├── SQLite 表结构创建
├── LanceDB 初始化
├── basic CRUD API
├── CLI: init, status, query, store
└── 测试：手动插入和查询一个 Project
```

## Phase 2: Extractor（Week 3-4）

```
目标：自动从外部源提取
├── Obsidian Markdown Parser
├── GitHub Commit Parser
├── Entity Recognizer (rule-based)
├── Relation Extractor
├── CLI: import, sync
└── 测试：从 Obsidian 导入 10 个文件
```

## Phase 3: Intelligence（Week 5-6）

```
目标：语义搜索 + 记忆构建
├── LanceDB 向量索引集成
├── Hybrid Search (RRF fusion)
├── LLM extraction fallback
├── Memory Builder (daily cron)
├── Short-term memory expiration
├── CLI: search, build, daily
└── 测试：语义搜索准确率 > 80%
```

## Phase 4: Agent API（Week 7-8）

```
目标：Agent 可调用的完整 API
├── /memory/hybrid 端点
├── /memory/traverse 图遍历
├── Graph visualization (optional)
├── Agent query protocol 文档
├── CLI: serve
├── Performance optimization
└── 测试：集成到 Frontend Agent 实际工作流
```

---

# 十、与 Sera OPCOS 其他层的集成

## 与 Agent 层的集成

```
Agent 启动时：
1. 调用 /memory/hybrid 获取项目上下文
2. 调用 /memory/traverse 获取关系网络
3. 将结果注入 System Prompt

Agent 工作时：
1. 每次决策 → 调用 /memory/store
2. 每次失败 → 调用 /memory/store (Experience)
3. 每次创建资产 → 调用 /memory/relate

Agent 结束时：
1. 触发 /memory/build 增量更新
```

## 与 Factory 层的集成

```
Factory 执行时：
1. 查询 Memory 获取历史经验
2. 查询 Memory 获取可用 Skill
3. 产出物自动关联到 Project

Factory 完成后：
1. 产出物 → Asset Entity
2. 流程 → Workflow Entity
3. 问题 → Experience Entity
```

## 与 Obsidian 的集成

```
双向同步：
1. Obsidian → Memory Engine (Extractor)
   - Markdown 文件变更自动触发提取
   - 生成 Entity 和 Relation

2. Memory Engine → Obsidian (可选)
   - 每日组织记忆写入 Obsidian 06_Daily/
   - 趋势分析写入 Obsidian 05_Archive/

3. Markdown 增强语法（可选）
   ```markdown
   <!-- sera-memory -->
   type: Decision
   related: project_tradespan_001
   importance: 0.9
   <!-- /sera-memory -->
   ```
```

---

## 附录 A: 为什么不用 Neo4j？

Neo4j 是优秀的产品，但 V1 不适合：

| 维度 | SQLite + CTE | Neo4j |
|------|-------------|-------|
| 安装 | 零配置 | 需要 Java + 服务 |
| 体积 | 单文件 MB 级 | 服务 GB 级 |
| 运维 | 无 | 需要监控、备份 |
| 学习曲线 | SQL 即用 | Cypher 新语言 |
| 分布式 | 不需要 V1 | 过度设计 |
| 向量 | 需外挂 | 需外挂 |

**CTE 限制：** SQLite 的递归 CTE 适合深度 ≤ 3 的图遍历。对于 Sera OPCOS V1 的规模（< 1000 Entity），这完全足够。当规模增长到需要深度图分析时，可升级到 Neo4j 或 PostgreSQL + pgRouting。

## 附录 B: 为什么不用 PostgreSQL？

PostgreSQL 是优秀的数据库，但 V1 不适合：

| 维度 | SQLite | PostgreSQL |
|------|--------|------------|
| 安装 | 零配置 | 需要安装服务 |
| 配置 | 无 | 需要配置用户、权限、网络 |
| 备份 | 复制文件 | pg_dump |
| 向量 | 无 | pgvector 扩展 |
| 适用场景 | 单机 / 边缘 | 多客户端 / 生产集群 |

**决策：** V1 阶段使用 SQLite + LanceDB 组合。当需要多 Agent 并行写入时，升级到 PostgreSQL + pgvector。

## 附录 C: 核心数据流图

```
                  ┌──────────────┐
                  │   Obsidian   │
                  │  (Markdown)  │
                  └──────┬───────┘
                         │ watch
                         ▼
                  ┌──────────────┐
                  │  Extractor   │
                  │  Pipeline    │
                  └──────┬───────┘
                         │ entities, relations, memories
         ┌───────────────┼───────────────────┐
         ▼               ▼                   ▼
  ┌────────────┐  ┌────────────┐  ┌──────────────────┐
  │   SQLite   │  │  LanceDB   │  │  Filesystem      │
  │  Entities  │  │  Vectors   │  │  Assets          │
  │  Relations │  │  (semantic)│  │  (blobs)         │
  │  Memories  │  │            │  │                  │
  │  FTS5      │  │            │  │                  │
  └────────────┘  └────────────┘  └──────────────────┘
         │               │                  │
         └───────────────┼──────────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  Memory      │
                  │  Builder     │  ← cron daily
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  Daily       │
                  │  Memory      │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  Agent API   │
                  │  /memory/*   │  ← Frontend Agent / Video Agent / ...
                  └──────────────┘
```

---

*Document Version: 1.0*
*Last Updated: 2026-08-21*
*Next: Sera Memory Engine Implementation Guide V1*